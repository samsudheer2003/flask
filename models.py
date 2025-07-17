import uuid
from datetime import datetime, timezone
from extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Salt + Pepper hashed
    create_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    phone_verified = db.Column(db.Boolean, nullable=False, default=False)

    todos = db.relationship(
        'ToDo',
        backref='user',
        lazy=True,
        primaryjoin="User.uid==ToDo.user_uid"
    )


class ToDo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    task = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.String(20), default="in progress", nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    modified_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    user_uid = db.Column(db.String(36), db.ForeignKey('user.uid', name='fk_todo_user_uid'), nullable=False)


class UserToken(db.Model):
    __tablename__ = "user_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_uid = db.Column(db.String(64), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    access_token_expiry = db.Column(db.DateTime(timezone=True), nullable=True)
    refresh_token = db.Column(db.Text, nullable=False)
    refresh_token_expiry = db.Column(db.DateTime(timezone=True), nullable=False)
    device_uuid = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserOTP(db.Model):
    __tablename__ = "user_otps"
    id = db.Column(db.Integer, primary_key=True)
    user_uid = db.Column(db.String, db.ForeignKey("user.uid"), nullable=False)
    otp_code = db.Column(db.String, nullable=False)
    purpose = db.Column(db.String, nullable=False)  # 'email_verification', 'phone_verification'
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship("User", backref=db.backref("otps", lazy=True))
