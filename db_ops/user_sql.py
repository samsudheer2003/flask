from models import db, User
from sqlalchemy import or_
from schemas.user_schemas import UserResponseSchema

def is_user_exists(username, email, mobile):
    return (
        User.query.filter(
            (User.username == username) |
            (User.email == email) |
            (User.mobile_number == mobile)
        ).first()
        is not None
    )

def insert_user(username, first_name, last_name, email, mobile, hashed_pw):
    user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        mobile_number=mobile,
        password=hashed_pw
    )
    db.session.add(user)
    db.session.commit()
    return user  

def get_user_by_username_or_email(identifier):
    return User.query.filter(
        or_(User.username == identifier, User.email == identifier)
    ).first()

def get_user_by_uid(uid):
    return User.query.filter_by(uid=uid).first()

def get_all_users_serialized():
    
    users = User.query.all()
    user_schema = UserResponseSchema(many=True)
    return user_schema.dump(users)

def update_verification_status(user_uid, verification_type):
    """
    Updates the email_verified or phone_verified field of the user.
    """
    user = get_user_by_uid(user_uid)
    if not user:
        return False

    if verification_type == "phone":
        user.phone_verified = True
    elif verification_type == "email":
        user.email_verified = True
    else:
        return False

    db.session.commit()
    return True
