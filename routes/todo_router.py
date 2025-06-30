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

todo_router = Blueprint('todo_router', __name__)


@todo_router.route('/', methods=['POST'])
@jwt_required()
def create_todo():
    """
    Create a new TODO item for the authenticated user.

    Expects:
        JSON body with:
            - task (str, required): Task description.
            - status (str, optional): One of ['pending', 'in_progress', 'completed', 'cancelled'].

    Returns:
        201: Todo created successfully.
        400: Validation failed.
        500: Internal server error.
    """
    schema = TodoCreateSchema()
    try:
        user_id = get_jwt_identity()
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
@jwt_required()
def get_todos():
    """
    Retrieve a list of TODOs for the authenticated user with optional filters.

    Query Parameters:
        - page (int): Page number for pagination.
        - per_page (int): Number of items per page.
        - status (str): Filter by status.
        - search (str): Search string to match task content.

    Returns:
        200: List of todos with pagination.
        400: Invalid query parameters.
        500: Internal server error.
    """
    query_schema = TodoListQuerySchema()
    try:
        user_id = get_jwt_identity()
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


@todo_router.route('/update', methods=['PUT'])
@jwt_required()
def update_todo():
    """
    Update a TODo item by its UID for the authenticated user.

    Query Parameter:
        - todo_uid (str, required): UID of the todo to update.

    Expects:
        JSON body with at least one of:
            - task (str): Updated task content.
            - status (str): Updated status.

    Returns:
        200: Todo updated successfully.
        400: Validation or missing parameter.
        403: Unauthorized to update this todo.
        404: Todo not found.
        500: Internal server error.
    """
    schema = TodoUpdateSchema()
    try:
        user_id = get_jwt_identity()
        todo_uid = request.args.get('todo_uid')
        if not todo_uid:
            return jsonify({'message': 'todo_uid query parameter is required'}), 400

        validated_data = schema.load(request.get_json() or {})
        response, status = update_todo_logic(todo_uid, user_id, validated_data)
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
@jwt_required()
def delete_todo():
    """
    Delete a TODo item by its UID for the authenticated user.

    Query Parameter:
        - todo_id (str, required): UID of the todo to delete.

    Returns:
        200: Todo deleted successfully.
        400: Missing todo_id parameter.
        403: Unauthorized to delete this todo.
        404: Todo not found.
        500: Internal server error.
    """
    try:
        user_uid = get_jwt_identity()
        todo_uid = request.args.get('todo_id')

        if not todo_uid:
            return jsonify({'message': 'todo_id query parameter is required'}), 400

        response, status = delete_todo_logic(todo_uid, user_uid)
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Delete todo endpoint error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
