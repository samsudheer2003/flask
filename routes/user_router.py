import logging
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from managers.user_manager import register_user_logic, login_user_logic
from schemas.user_schemas import UserRegistrationSchema, UserLoginSchema

user_router = Blueprint('user_router', __name__)


@user_router.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    Expects:
        JSON payload with the following fields:
            - username (str)
            - first_name (str)
            - last_name (str)
            - email (str)
            - mobile_number (str)
            - password (str)

    Returns:
        201: Registration successful with user details.
        400: Validation errors in request data.
        409: Conflict  user already exists.
        500: Internal server error.
    """
    schema = UserRegistrationSchema()
    try:
        validated_data = schema.load(request.get_json() or {})
        response, status = register_user_logic(validated_data)
        return jsonify(response), status
    except ValidationError as err:
        return jsonify({
            'message': 'Validation failed',
            'errors': err.messages
        }), 400
    except Exception as e:
        logging.error(f"Registration endpoint error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@user_router.route('/login', methods=['POST'])
def login():
    """
    Authenticate an existing user and generate a JWT token.

    Expects:
        JSON payload with:
            - username (or email) (str)
            - password (str)

    Returns:
        200: Login successful with access token and user info.
        400: Validation errors in request data.
        401: Unauthorized invalid credentials.
        500: Internal server error.
    """
    schema = UserLoginSchema()
    try:
        validated_data = schema.load(request.get_json() or {})
        response, status = login_user_logic(validated_data)
        return jsonify(response), status
    except ValidationError as err:
        return jsonify({
            'message': 'Validation failed',
            'errors': err.messages
        }), 400
    except Exception as e:
        logging.error(f"Login endpoint error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
