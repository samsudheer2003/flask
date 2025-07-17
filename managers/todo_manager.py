import logging
from flask import request
from models import UserToken
from db_ops.todo_sql import (
    insert_todo, 
    get_todos_by_user_with_filters,
    get_todo_by_uid,
    update_todo_by_uid,
    delete_todo_by_uid
)
from schemas.todo_schemas import TodoBasicResponseSchema
from utils import extract_mandatory_headers

def _validate_device_uuid(user_uid, device_uuid):
    token_entry = UserToken.query.filter_by(user_uid=user_uid, device_uuid=device_uuid).first()
    if not token_entry:
        logging.warning(f"Device UUID mismatch for user_uid: {user_uid}")
        return False
    return True


def create_todo_logic(validated_data):
    try:
        headers, error_response, status = extract_mandatory_headers()
        if error_response:
            return error_response, status

        user_uid = validated_data['user_id']
        device_uuid = headers['Device-UUID']

        if not _validate_device_uuid(user_uid, device_uuid):
            return {'message': 'Unauthorized device'}, 401

        task = validated_data['task']
        status = validated_data.get('status', 'pending')

        logging.info(f"Creating todo for user_uid: {user_uid}, task: {task}, status: {status}")

        todo = insert_todo(task=task, user_uid=user_uid, status=status)
        todo_schema = TodoBasicResponseSchema()

        return {
            'message': 'Todo created successfully',
            'todo': todo_schema.dump(todo)
        }, 201

    except Exception as e:
        logging.error(f"Todo creation error: {str(e)}")
        return {'message': 'Internal server error'}, 500


def get_todos_logic(user_uid, query_params):
    try:
        headers, error_response, status = extract_mandatory_headers()
        if error_response:
            return error_response, status

        device_uuid = headers['Device-UUID']
        if not _validate_device_uuid(user_uid, device_uuid):
            return {'message': 'Unauthorized device'}, 401

        todos, total_count = get_todos_by_user_with_filters(
            user_uid=user_uid,
            page=query_params.get('page', 1),
            per_page=query_params.get('per_page', 10),
            status=query_params.get('status'),
            search=query_params.get('search')
        )

        todo_schema = TodoBasicResponseSchema(many=True)
        serialized_todos = todo_schema.dump(todos)

        return {
            'todos': serialized_todos,
            'pagination': {
                'page': query_params.get('page', 1),
                'per_page': query_params.get('per_page', 10),
                'total': total_count,
                'pages': (total_count + query_params.get('per_page', 10) - 1) // query_params.get('per_page', 10)
            }
        }, 200

    except Exception as e:
        logging.error(f"Fetch todos error: {str(e)}")
        return {'message': 'Internal server error'}, 500


def update_todo_logic(todo_uid, user_uid, validated_data):
    try:
        headers, error_response, status = extract_mandatory_headers()
        if error_response:
            return error_response, status

        device_uuid = headers['Device-UUID']
        if not _validate_device_uuid(user_uid, device_uuid):
            return {'message': 'Unauthorized device'}, 401

        todo = get_todo_by_uid(todo_uid)
        if not todo:
            return {'message': 'Todo not found'}, 404

        if todo.user_uid != user_uid:
            return {'message': 'Unauthorized to update this todo'}, 403

        updated_todo = update_todo_by_uid(todo_uid, validated_data)
        todo_schema = TodoBasicResponseSchema()

        return {
            'message': 'Todo updated successfully',
            'todo': todo_schema.dump(updated_todo)
        }, 200

    except Exception as e:
        logging.error(f"Todo update error: {str(e)}")
        return {'message': 'Internal server error'}, 500


def delete_todo_logic(todo_uid, user_uid):
    try:
        headers, error_response, status = extract_mandatory_headers()
        if error_response:
            return error_response, status

        device_uuid = headers['Device-UUID']
        if not _validate_device_uuid(user_uid, device_uuid):
            return {'message': 'Unauthorized device'}, 401

        todo = get_todo_by_uid(todo_uid)
        if not todo:
            return {'message': 'Todo not found'}, 404

        if todo.user_uid != user_uid:
            return {'message': 'Unauthorized to delete this todo'}, 403

        delete_todo_by_uid(todo_uid)
        return {'message': 'Todo deleted successfully'}, 200

    except Exception as e:
        logging.error(f"Todo deletion error: {str(e)}")
        return {'message': 'Internal server error'}, 500
