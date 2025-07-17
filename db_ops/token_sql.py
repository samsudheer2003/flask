from models import db, UserToken
from datetime import datetime, timedelta

def store_tokens(user_id, access_token, refresh_token, device_name, device_uuid, access_expires_in=15, refresh_expires_in=30, created_at=None):
    """Store access and refresh tokens with device details."""
    access_expiry = datetime.utcnow() + timedelta(minutes=access_expires_in)
    refresh_expiry = datetime.utcnow() + timedelta(days=refresh_expires_in)

    token_entry = UserToken(
        user_uid=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expiry=access_expiry,
        refresh_token_expiry=refresh_expiry,
    
        device_uuid=device_uuid,
        created_at=created_at or datetime.utcnow()
    )

    db.session.add(token_entry)
    db.session.commit()



def get_user_id_from_refresh_token(refresh_token: str):
    """Return the user ID based on the given refresh token, if valid and not expired."""
    token = UserToken.query.filter_by(refresh_token=refresh_token).first()

    if token and token.refresh_expires_at > datetime.utcnow():
        return token.user_id
    return None

def update_access_token(user_id, device_uuid, new_access_token, access_expires_in=15):
    """Update the access token and expiry for the given user and device."""
    token_entry = UserToken.query.filter_by(user_id=user_id, device_uuid=device_uuid).first()
    
    if token_entry:
        token_entry.access_token = new_access_token
        token_entry.access_expires_at = datetime.utcnow() + timedelta(minutes=access_expires_in)
        db.session.commit()
        return True
    return False