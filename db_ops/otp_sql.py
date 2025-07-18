from datetime import datetime, timezone
from extensions import db
from models import UserOTP


def save_otp(user_uid, otp_code, purpose, expires_at):
    """
    Save a new OTP record for the user.

    """
    otp_entry = UserOTP(
        user_uid=user_uid,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=expires_at
    )
    db.session.add(otp_entry)
    db.session.commit()


def get_valid_otp(user_uid, otp_code, purpose):
    """
    Retrieve a valid and unused OTP that hasn't expired.
    """
    now = datetime.now(timezone.utc)
    return UserOTP.query.filter_by(
        user_uid=user_uid,
        otp_code=otp_code,
        purpose=purpose,
        is_used=False
    ).filter(UserOTP.expires_at >= now).first()


def mark_otp_used(otp_entry):
    """
    Mark a given OTP as used.
    """
    otp_entry.is_used = True
    db.session.commit()
