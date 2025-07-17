import logging
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from managers.todo_manager import (
    create_todo_logic,
    get_todos_logic,
    update_todo_logic,
    delete_todo_logic
)
from schemas.todo_schemas import (
    TodoCreateSchema,
    TodoUpdateSchema,
    TodoListQuerySchema
)
from utils import extract_mandatory_headers

todo_router = Blueprint('todo_router', __name__)

@todo_router.route('/', methods=['POST'])
@jwt_required()
def create_todo():
    try:
        # Validate headers
        headers, error_response, status = extract_mandatory_headers()
        if error_response:
            return error_response, status

        user_id = get_jwt_identity()
        schema = TodoCreateSchema()
        validated_data = schema.load(request.get_json() or {})
        validated_data['user_id'] = user_id

        response, status = create_todo_logic(validated_data)
        return jsonify(response), status
    except ValidationError as err:
        return jsonify({
            'message': 'Validation failed',
            'errors': err.messages
        }), 400
    except Exception as e:
        logging.error(f"[CREATE TODO ERROR] {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@todo_router.route('/', methods=['GET'])
@jwt_required()
def get_todos():
    try:
        headers, error_response, status = extract_mandatory_headers()
        if error_response:
            return error_response, status

        user_id = get_jwt_identity()
        query_schema = TodoListQuerySchema()
        query_params = query_schema.load(request.args.to_dict())
        response, status = get_todos_logic(user_id, query_params)
        return jsonify(response), status
    except ValidationError as err:
        return jsonify({
            'message': 'Invalid query parameters',
            'errors': err.messages
        }), 400
    except Exception as e:
        logging.error(f"[GET TODOS ERROR] {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@todo_router.route('/update', methods=['PUT'])
@jwt_required()
def update_todo():
    try:
        headers, error_response, status = extract_mandatory_headers()
        if error_response:
            return error_response, status

        user_id = get_jwt_identity()
        todo_uid = request.args.get('todo_uid')
        if not todo_uid:
            return jsonify({'message': 'todo_uid query parameter is required'}), 400

        schema = TodoUpdateSchema()
        validated_data = schema.load(request.get_json() or {})
        response, status = update_todo_logic(todo_uid, user_id, validated_data)
        return jsonify(response), status
    except ValidationError as err:
        return jsonify({
            'message': 'Validation failed',
            'errors': err.messages
        }), 400
    except Exception as e:
        logging.error(f"[UPDATE TODO ERROR] {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@todo_router.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_todo():
    try:
        headers, error_response, status = extract_mandatory_headers()
        if error_response:
            return error_response, status

        user_uid = get_jwt_identity()
        todo_uid = request.args.get('todo_id')

        if not todo_uid:
            return jsonify({'message': 'todo_id query parameter is required'}), 400

        response, status = delete_todo_logic(todo_uid, user_uid)
        return jsonify(response), status
    except Exception as e:
        logging.error(f"[DELETE TODO ERROR] {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
