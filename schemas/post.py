from marshmallow import Schema, fields, validate, post_dump

from schemas.user import UserSchema
from schemas.pagination import PaginationSchema


class PostSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Int(dump_only=True)
    body = fields.Str(required=True, validate=[validate.Length(max=500, min=1)])
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    author = fields.Nested(UserSchema, attribute='user', dump_only=True, exclude=('email',))
    # the only=['id', 'username'] results in displaying only the id and the username of the author
    # alternately we can also specify excluding the email using exclude=(email,) attribute.


class PostPaginationSchema(PaginationSchema):
    data = fields.Nested(PostSchema, attribute='items', many=True)
