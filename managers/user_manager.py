import logging
from flask_bcrypt import Bcrypt
from db_ops.user_sql import (
    is_user_exists,
    insert_user,
    get_user_by_username_or_email
)
from schemas.user_schemas import UserBasicResponseSchema
from flask_jwt_extended import create_access_token
from datetime import timedelta

bcrypt = Bcrypt()

def register_user_logic(validated_data):
    """
    Handles user registration logic.

    Args:
        validated_data (dict): User details including username, email, password, etc.

    Returns:
        tuple: JSON response with success or error message, and HTTP status code.
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

        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        insert_user(username, first_name, last_name, email, mobile_number, hashed_pw)

        user = get_user_by_username_or_email(username)
        user_schema = UserBasicResponseSchema()
        return {
            'message': 'Registered successfully',
            'user': user_schema.dump(user)
        }, 201

    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return {'message': 'Internal server error'}, 500


def login_user_logic(validated_data):
    """
    Handles user login and JWT token generation.

    Args:
        validated_data (dict): Contains username/email and password.

    Returns:
        tuple: JSON response including access_token on success, or error message and status.
    """
    try:
        login_input = validated_data['username']
        password = validated_data['password']

        user = get_user_by_username_or_email(login_input)
        if user and bcrypt.check_password_hash(user.password, password):
            user_schema = UserBasicResponseSchema()

            access_token = create_access_token(
                identity=str(user.uid),
                expires_delta=timedelta(days=1)
            )

            return {
                'message': 'Login successful',
                'user': user_schema.dump(user),
                'access_token': access_token
            }, 200

        return {'message': 'Invalid username/email or password'}, 401

    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return {'message': 'Internal server error'}, 500
