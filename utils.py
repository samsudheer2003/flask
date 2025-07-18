import random
import os
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from twilio.rest import Client
from models import UserToken

def extract_mandatory_headers():
    """
    Extract and validate mandatory headers from the request.

    """
    content_type = request.headers.get("Content-Type")
    device_name = request.headers.get("Device-Name")
    device_uuid = request.headers.get("Device-UUID")

    if not content_type or not device_name or not device_uuid:
        return None, jsonify({
            "message": "Missing required headers",
            "required_headers": ["Content-Type", "Device-Name", "Device-UUID"]
        }), 400

    return {
        "Content-Type": content_type,
        "Device-Name": device_name,
        "Device-UUID": device_uuid
    }, None, None


def generate_otp(length=6):
    """
    Generate a numeric OTP of specified length.

    """
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def send_otp_via_sms(phone_number, otp_code):
    """
    Send OTP via Twilio SMS.

    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"Your OTP code is: {otp_code}",
        from_=from_number,
        to=phone_number
    )
    return message.sid


def token_required_with_device_check():
    """
    Custom decorator to validate JWT token and match device UUID.

    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            headers, error_response, status = extract_mandatory_headers()
            if error_response:
                return error_response, status

            verify_jwt_in_request()
            current_user_uid = get_jwt_identity()
            device_uuid = headers["Device-UUID"]

            token_in_db = UserToken.query.filter_by(
                user_uid=current_user_uid,
                device_uuid=device_uuid
            ).first()

            if not token_in_db:
                return jsonify({"message": "Invalid token or device UUID mismatch"}), 401

            return fn(*args, **kwargs)
        return decorator
    return wrapper
