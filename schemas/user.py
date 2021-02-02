from marshmallow import fields, Schema

from encrypt import encrypt_pass

class UserSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Method(required=True, deserialize='load_password')
    email = fields.Email(required=True)

    def load_password(self, value):
        return encrypt_pass(value)

