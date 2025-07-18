import logging
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token
from datetime import datetime, timezone

from models import db, UserToken, User
from managers.user_manager import register_user_logic, login_user_logic, verify_otp_logic,resend_otp_logic
from schemas.user_schemas import UserRegistrationSchema, UserLoginSchema
from utils import extract_mandatory_headers


user_router = Blueprint('user_router', __name__)

# ------------------ Register Route ------------------
@user_router.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    """
    schema = UserRegistrationSchema()
    try:
        validated_data = schema.load(request.get_json() or {})
        response, status = register_user_logic(validated_data)
        return jsonify(response), status
    except ValidationError as err:
        return jsonify({'message': 'Validation failed', 'errors': err.messages}), 400
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


# ------------------ Login Route ------------------
@user_router.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and return JWT access & refresh tokens.
    """
    headers, error_response, status = extract_mandatory_headers()
    if error_response:
        return error_response, status

    schema = UserLoginSchema()
    try:
        validated_data = schema.load(request.get_json() or {})
        response, status = login_user_logic(
            validated_data,
            headers["Device-Name"],
            headers["Device-UUID"]
        )
        return jsonify(response), status
    except ValidationError as err:
        return jsonify({'message': 'Validation failed', 'errors': err.messages}), 400
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


# ------------------ Refresh Token Route ------------------
@user_router.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Generate a new access token using a valid refresh token.
    """
    headers, error_response, status = extract_mandatory_headers()
    if error_response:
        return error_response, status

    data = request.get_json() or {}
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({"message": "Missing refresh token"}), 400

    try:
        token_entry = UserToken.query.filter_by(
            refresh_token=refresh_token,
            device_uuid=headers["Device-UUID"]
        ).first()

        if not token_entry:
            return jsonify({"message": "Invalid refresh token or device"}), 401

        if token_entry.refresh_token_expiry < datetime.now(timezone.utc):
            return jsonify({"message": "Refresh token expired"}), 401

        user = User.query.get(token_entry.user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        new_access_token = create_access_token(identity=user.id)

        # Update token entry in the DB
        token_entry.access_token = new_access_token
        token_entry.access_token_expiry = datetime.now(timezone.utc)
        db.session.commit()

        return jsonify({
            "access_token": new_access_token,
            "message": "Access token refreshed"
        }), 200

    except Exception as e:
        logging.error(f"Refresh token error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# ------------------ OTP Verification Route ------------------
@user_router.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verifies OTP for phone or email.
    
    """
    try:
        data = request.get_json() or {}
        response, status = verify_otp_logic(data)
        return jsonify(response), status
    except Exception as e:
        logging.error(f"OTP verification route error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@user_router.route('/resend-otp', methods=['POST'])
def resend_otp():
    """
    Resend OTP to the user’s phone or email.
    """
    try:
        data = request.get_json() or {}
        response, status = resend_otp_logic(data)
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Resend OTP route error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
