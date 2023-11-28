from marshmallow import Schema, fields, post_load
from datetime import datetime
import uuid


class UserClassroomSchema(Schema):
    id_classroom = fields.UUID()
    is_teacher = fields.Str()


class UserSchema(Schema):
    id = fields.UUID(load_default=uuid.uuid4)
    pseudo = fields.Str(required=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    email = fields.Email(required=True)
    is_admin = fields.Boolean(required=True)
    birthdate = fields.Date(required=True)
    address = fields.Str()

    classrooms = fields.List(fields.Nested(UserClassroomSchema), default=list())
    created_at = fields.DateTime()

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


class User:
    def __init__(self, id, pseudo, firstname, lastname, email, password, is_admin, birthdate, address="", classrooms=[]):
        self.id = id
        self.pseudo = pseudo
        self.firstname = firstname
        self.lastname = lastname

        self.email = email
        self.is_admain = is_admin
        self.classrooms = classrooms
        self.birthdate = birthdate
        self.address = address
        self.created_at = datetime.now()
        self.last_update = datetime.now()

