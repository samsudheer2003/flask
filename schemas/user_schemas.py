from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import User
import re

class UserRegistrationSchema(Schema):
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, error="Username must be at least 3 characters"),
            validate.Regexp(r'^[a-zA-Z0-9]+$', error="Username must be alphanumeric")
        ]
    )
    first_name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, error="First name must be at least 2 characters"),
            validate.Regexp(r'^[a-zA-Z]+$', error="First name must contain only letters")
        ]
    )
    last_name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, error="Last name must be at least 2 characters"),
            validate.Regexp(r'^[a-zA-Z]+$', error="Last name must contain only letters")
        ]
    )
    email = fields.Email(required=True, error_messages={"invalid": "Invalid email address"})
    mobile_number = fields.Str(
        required=True,
        validate=validate.Regexp(r'^\d{10}$', error="Mobile number must be exactly 10 digits")
    )
    password = fields.Str(required=True, validate=validate.Length(min=6))

    @validates('password')
    def validate_password(self, value):
        if value.lower() == value:
            raise ValidationError("Password must contain at least one uppercase letter")
        if value.upper() == value:
            raise ValidationError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one number")

class UserLoginSchema(Schema):
    username = fields.Str(required=True, error_messages={"required": "Username/email is required"})
    password = fields.Str(required=True, error_messages={"required": "Password is required"})

class UserResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password',)  

class UserBasicResponseSchema(Schema):
    uid = fields.Str()
    username = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
