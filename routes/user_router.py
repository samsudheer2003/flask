import logging
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from managers.user_manager import register_user_logic, login_user_logic
from schemas.user_schemas import UserRegistrationSchema, UserLoginSchema

user_router = Blueprint('user_router', __name__)

@user_router.route('/register', methods=['POST'])
def register():
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
