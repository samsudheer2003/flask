import logging
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
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

todo_router = Blueprint('todo_router', __name__)


@todo_router.route('/', methods=['POST'])
def create_todo():
    schema = TodoCreateSchema()
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'user_id query parameter is required'}), 400

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
        logging.error(f"Create todo endpoint error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
    

@todo_router.route('/', methods=['GET'])
def get_todos():
    query_schema = TodoListQuerySchema()
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'message': 'user_id query parameter is required'}), 400

        query_params = query_schema.load(request.args.to_dict())
        response, status = get_todos_logic(user_id, query_params)
        return jsonify(response), status
    except ValidationError as err:
        return jsonify({
            'message': 'Invalid query parameters',
            'errors': err.messages
        }), 400
    except Exception as e:
        logging.error(f"Get todos endpoint error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
    

@todo_router.route('/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    schema = TodoUpdateSchema()
    try:
        user_id = request.headers.get('User-Id')
        if not user_id:
            return jsonify({'message': 'User-Id header is required'}), 400

        validated_data = schema.load(request.get_json() or {})
        response, status = update_todo_logic(todo_id, user_id, validated_data)
        return jsonify(response), status
    except ValidationError as err:
        return jsonify({
            'message': 'Validation failed',
            'errors': err.messages
        }), 400
    except Exception as e:
        logging.error(f"Update todo endpoint error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
    

@todo_router.route('/delete', methods=['DELETE'])
def delete_todo():
    try:
        user_uid = request.args.get('user_id')
        todo_uid = request.args.get('todo_id')

        if not user_uid or not todo_uid:
            return jsonify({'message': 'user_id and todo_id query parameters are required'}), 400

        response, status = delete_todo_logic(todo_uid, user_uid)
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Delete todo endpoint error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
