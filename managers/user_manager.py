import os
import logging
import random
from datetime import timedelta, datetime, timezone
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from dotenv import load_dotenv
from db_ops.otp_sql import get_valid_otp, mark_otp_used
from db_ops.user_sql import update_verification_status



from db_ops.user_sql import (
    is_user_exists,
    insert_user,
    get_user_by_username_or_email
)
from db_ops.token_sql import (
    store_tokens,
    get_user_id_from_refresh_token,
    update_access_token
)
from db_ops.otp_sql import save_otp
from schemas.user_schemas import UserBasicResponseSchema
from utils import send_otp_via_sms


# Load environment and init bcrypt
load_dotenv()
PEPPER_SECRET = os.getenv("PEPPER_SECRET", "")
bcrypt = Bcrypt()


def generate_otp():
    """Generates a 6-digit OTP as string."""
    return str(random.randint(100000, 999999))


def register_user_logic(validated_data):
    """
    Handles user registration logic:
    - Check for duplicate user
    - Hash password using salt + pepper
    - Save user to DB
    - Generate and send OTP via Twilio
    """
    try:
        username = validated_data['username']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        email = validated_data['email']
        mobile_number = validated_data['mobile_number']
        password = validated_data['password']

        if is_user_exists(username=username, email=email, mobile=mobile_number):
            logging.warning(f"User already exists - username: {username}, email: {email}, mobile: {mobile_number}")
            return {'message': 'User already exists with provided details'}, 409

        # Salt + Pepper Hashing
        peppered_pw = password + PEPPER_SECRET
        hashed_pw = bcrypt.generate_password_hash(peppered_pw).decode('utf-8')

        # Insert User
        insert_user(username, first_name, last_name, email, mobile_number, hashed_pw)

        # Get created user
        user = get_user_by_username_or_email(username)
        user_schema = UserBasicResponseSchema()

        # Generate OTP
        otp = generate_otp()

        # Save OTP to DB with 5 min expiry
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        save_otp(user.uid, otp, "phone", expires_at)

        # Send OTP using Twilio
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
    Handles user login, password verification, and token generation.
    """
    try:
        login_input = validated_data['username']
        password = validated_data['password']

        user = get_user_by_username_or_email(login_input)
        if user:
            peppered_pw = password + PEPPER_SECRET
            if bcrypt.check_password_hash(user.password, peppered_pw):
                user_schema = UserBasicResponseSchema()

                access_token = create_access_token(
                    identity=str(user.uid),
                    expires_delta=timedelta(minutes=15)
                )
                refresh_token = create_refresh_token(
                    identity=str(user.uid),
                    expires_delta=timedelta(days=7)
                )

                store_tokens(
                    user_id=user.uid,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    device_name=device_name,
                    device_uuid=device_uuid,
                    created_at=datetime.now(timezone.utc)
                )

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
    Generates new access token from refresh token and validates device.
    """
    try:
        user_id = get_user_id_from_refresh_token(refresh_token, device_uuid)
        if not user_id:
            return {'message': 'Invalid or expired refresh token or mismatched device UUID'}, 401

        new_access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(minutes=15)
        )

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
    Verifies the OTP for the user and updates their verification status (email/phone).
    """
    try:
        user_id = data.get("user_id")
        otp = data.get("otp")
        verification_type = data.get("type")  # 'phone' or 'email'

        if not user_id or not otp or not verification_type:
            return {'message': 'Missing user_id, otp, or type (phone/email)'}, 400

        otp_record = get_valid_otp(user_id, otp, verification_type)
        if not otp_record:
            return {'message': 'Invalid or expired OTP'}, 400

        # Mark OTP as used
        mark_otp_used(otp_record.id)

        # Update verification status
        update_verification_status(user_id, verification_type)

        return {'message': f'{verification_type.capitalize()} verified successfully'}, 200

    except Exception as e:
        logging.error(f"OTP verification error: {str(e)}")
        return {'message': 'Internal server error'}, 500
