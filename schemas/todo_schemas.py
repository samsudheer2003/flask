from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import ToDo
from datetime import datetime

STATUS_VALUES = ["pending", "in_progress", "completed", "cancelled"]

class TodoCreateSchema(Schema):
    task = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500, error="Task must be between 1 and 500 characters."),
        error_messages={"required": "Task is required."}
    )
    status = fields.Str(
        load_default="pending",
        validate=validate.OneOf(STATUS_VALUES, error="Invalid status value.")
    )


class TodoUpdateSchema(Schema):
    task = fields.Str(
        validate=validate.Length(min=1, max=500, error="Task must be between 1 and 500 characters."),
        load_default=None
    )
    status = fields.Str(
        load_default=None,
        validate=validate.OneOf(STATUS_VALUES, error="Invalid status value.")
    )

    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        if not any(data.values()):
            raise ValidationError("At least one field (task or status) must be provided.")


class TodoListQuerySchema(Schema):
    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1, error="Page must be at least 1.")
    )
    per_page = fields.Int(
        load_default=10,
        validate=validate.Range(min=1, max=100, error="Per page must be between 1 and 100.")
    )
    status = fields.Str(
        load_default=None,
        validate=validate.OneOf(STATUS_VALUES, error="Invalid status filter.")
    )
    search = fields.Str(
        load_default=None,
        validate=validate.Length(max=100, error="Search term must be 100 characters or less.")
    )


class TodoResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ToDo
        load_instance = True
        include_fk = True

    created_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    updated_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S', allow_none=True)


class TodoBasicResponseSchema(Schema):
    id = fields.Int()
    uid = fields.Str()
    task = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    updated_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S', allow_none=True)
