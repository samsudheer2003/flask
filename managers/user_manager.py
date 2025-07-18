import os
import logging
import random
from datetime import datetime, timedelta, timezone

from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from dotenv import load_dotenv

from db_ops.user_sql import (
    is_user_exists,
    insert_user,
    get_user_by_username_or_email,
    update_verification_status,
    get_user_by_uid
)
from db_ops.token_sql import (
    store_tokens,
    get_user_id_from_refresh_token,
    update_access_token
)
from db_ops.otp_sql import (
    save_otp,
    get_valid_otp,
    mark_otp_used,
    mark_all_user_otps_used
)
from schemas.user_schemas import UserBasicResponseSchema
from utils import send_otp_via_sms

# Load .env config
load_dotenv()
PEPPER_SECRET = os.getenv("PEPPER_SECRET", "")
bcrypt = Bcrypt()


def generate_otp():
    """Generate a 6-digit OTP as a string."""
    return str(random.randint(100000, 999999))


def register_user_logic(validated_data):
    """
    Handles user registration:
    - Hash password with salt + pepper
    - Save user
    - Generate & save OTP
    - Send OTP to phone
    """
    try:
        username = validated_data['username']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        email = validated_data['email']
        mobile_number = validated_data['mobile_number']
        password = validated_data['password']

        if is_user_exists(username=username, email=email):
            return {'message': 'User already exists'}, 409

        # Hash password with salt + pepper
        peppered_pw = password + PEPPER_SECRET
        hashed_pw = bcrypt.generate_password_hash(peppered_pw).decode('utf-8')

        # Save user
        insert_user(username, first_name, last_name, email, mobile_number, hashed_pw)
        user = get_user_by_username_or_email(username)
        user_schema = UserBasicResponseSchema()

        # Generate OTP and send via SMS
        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        save_otp(user.uid, otp, "phone", expires_at)
        send_otp_via_sms(mobile_number, otp)

        return {
            'message': 'Registered successfully. OTP sent to your phone.',
            'user': user_schema.dump(user)
        }, 201

    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return {'message': 'Internal server error'}, 500


def login_user_logic(validated_data, device_name, device_uuid):
    """
    Verifies user credentials and returns access & refresh tokens.
    """
    try:
        login_input = validated_data['username']
        password = validated_data['password']
        user = get_user_by_username_or_email(login_input)

        if user:
            peppered_pw = password + PEPPER_SECRET
            if bcrypt.check_password_hash(user.password, peppered_pw):
                access_token = create_access_token(identity=str(user.uid), expires_delta=timedelta(minutes=15))
                refresh_token = create_refresh_token(identity=str(user.uid), expires_delta=timedelta(days=7))

                store_tokens(user.uid, access_token, refresh_token, device_name, device_uuid, datetime.now(timezone.utc))
                user_schema = UserBasicResponseSchema()

                return {
                    'message': 'Login successful',
                    'user': user_schema.dump(user),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, 200

        return {'message': 'Invalid username/email or password'}, 401

    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return {'message': 'Internal server error'}, 500


def refresh_token_logic(refresh_token, device_uuid):
    """
    Refresh access token using refresh token & device validation.
    """
    try:
        user_id = get_user_id_from_refresh_token(refresh_token, device_uuid)
        if not user_id:
            return {'message': 'Invalid or expired refresh token or mismatched device UUID'}, 401

        new_access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(minutes=15))
        update_access_token(user_id, device_uuid, new_access_token)

        return {
            'message': 'Token refreshed successfully',
            'access_token': new_access_token
        }, 200

    except Exception as e:
        logging.error(f"Refresh token error: {str(e)}")
        return {'message': 'Internal server error'}, 500


def verify_otp_logic(data):
    """
    Verify OTP for phone/email and update verification status.
    """
    try:
        user_id = data.get("user_id")
        otp = data.get("otp")
        verification_type = data.get("type")  # phone/email

        if not user_id or not otp or not verification_type:
            return {'message': 'Missing user_id, otp, or type (phone/email)'}, 400

        otp_record = get_valid_otp(user_id, otp, verification_type)
        if not otp_record:
            return {'message': 'Invalid or expired OTP'}, 400

        mark_otp_used(otp_record)
        update_verification_status(user_id, verification_type)

        return {'message': f'{verification_type.capitalize()} verified successfully'}, 200

    except Exception as e:
        logging.error(f"OTP verification error: {str(e)}")
        return {'message': 'Internal server error'}, 500


def resend_otp_logic(data):
    """
    Resends OTP to user's phone or email.
    """
    try:
        user_id = data.get("user_id")
        verification_type = data.get("type")

        if not user_id or verification_type not in ['phone', 'email']:
            return {'message': 'Missing user_id or type (phone/email)'}, 400

        # Fetch user contact details
        user = get_user_by_uid(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        mark_all_user_otps_used(user_id, verification_type)
        save_otp(user_id, otp, verification_type, expires_at)

        if verification_type == 'phone':
            send_otp_via_sms(user.mobile_number, otp)
        

        return {'message': f'OTP resent to your {verification_type}'}, 200

    except Exception as e:
        logging.error(f"Resend OTP error: {str(e)}")
        return {'message': 'Internal server error'}, 500
