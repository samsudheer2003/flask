import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import Enum
db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = (
        db.UniqueConstraint('email', name='uq_user_email'),
        db.UniqueConstraint('username', name='uq_user_username'),
        db.UniqueConstraint('uid', name='uq_user_uid'),
    )

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), nullable=False, unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    create_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    todos = db.relationship('ToDo', backref='user', lazy=True, primaryjoin="User.uid==foreign(ToDo.user_uid)")


class ToDo(db.Model):
    __tablename__ = 'todo'
    __table_args__ = (
        db.UniqueConstraint('uid', name='uq_todo_uid'),
    )

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    task = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    user_uid = db.Column(db.String(36), db.ForeignKey('user.uid', name='fk_todo_user_uid'), nullable=False)
    status = db.Column(db.String(20),nullable=False,default='pending',server_default='pending')

