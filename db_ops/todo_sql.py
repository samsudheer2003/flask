from models import db, ToDo, User
from sqlalchemy import and_, or_
from datetime import datetime

def insert_todo(task, user_uid, status='pending'):
    todo = ToDo(task=task, user_uid=user_uid, status=status)
    db.session.add(todo)
    db.session.commit()
    return todo


def get_todos_by_user(user_uid):
    return ToDo.query.filter_by(user_uid=user_uid).order_by(ToDo.created_at.desc()).all()

def get_todos_by_user_with_filters(user_uid, page=1, per_page=10, status=None, search=None):
    query = ToDo.query.filter_by(user_uid=user_uid)

    if status:
        query = query.filter(ToDo.status == status)

    if search:
        query = query.filter(ToDo.task.ilike(f'%{search}%'))

    total_count = query.count()

    todos = query.order_by(ToDo.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    ).items

    return todos, total_count


def get_todo_by_id(todo_id):
    
    return ToDo.query.filter_by(id=todo_id).first()

def update_todo_by_uid(todo_uid, update_data):
    todo = ToDo.query.filter_by(uid=todo_uid).first()
    if not todo:
        return None

    if 'task' in update_data and update_data['task'] is not None:
        todo.task = update_data['task']

    if 'status' in update_data and update_data['status'] is not None:
        todo.status = update_data['status']

    todo.updated_at = datetime.utcnow()
    db.session.commit()
    return todo



def get_user_by_uid(user_uid):
   
    return User.query.filter_by(uid=user_uid).first()

def get_todo_by_uid(todo_uid):
    return ToDo.query.filter_by(uid=todo_uid).first()

def delete_todo_by_uid(todo_uid):
    todo = get_todo_by_uid(todo_uid)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return True
    return False
