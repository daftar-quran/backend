import datetime
import json

from daftar_common.http_response import HttpResponse
from daftar_common.models.classrooms import Classroom, ClassroomRoles
from daftar_common.models.users import User
from pydantic import BaseModel, ValidationError


class TemporaryTeacherRole(BaseModel):
    access_from: datetime.date
    access_until: datetime.date


class Metadata(BaseModel):
    temporary: TemporaryTeacherRole


class SwitchRolePayload(BaseModel):
    user_id: str
    role: ClassroomRoles
    meta: Metadata = {}


def switch_roles(event, classroom_id, users_table, classrooms_table):

    try:
        payload = None
        body = event.get("body")
        if body:
            payload = json.loads(body)
    except Exception as e:
        print(e)
        return HttpResponse.bad_request(error="Could not decode JSON body")

    # Data Validation
    try:
        switch_role_payload = SwitchRolePayload(**payload)
    except ValidationError as err:
        return HttpResponse.bad_request(error=err.errors())

    classroom = classrooms_table.get_item_by_id(classroom_id)
    if not classroom:
        return HttpResponse.not_found(error="Classroom not found")

    try:
        classroom = Classroom(**classroom)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")
    # Update classroom Table

    user_id = switch_role_payload.user_id

    desired_role = switch_role_payload.role

    # Update classroom
    classroom.switch_role_to_user(user_id=user_id, desired_role=desired_role)

    try:
        classrooms_table.update_item_by_id(
            classroom_id, classroom.model_dump(mode="json")
        )
    except Exception as e:
        return HttpResponse.internal_error(error=f"Unknown Error : {e}")

    #  Update Users table
    result = users_table.get_item_by_id(user_id)
    if not result:
        return HttpResponse.not_found(error="User not found")

    try:
        user = User(**result)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")

    #
    user.update_classroom_role(classroom_id=classroom_id, role=desired_role.value)

    try:
        users_table.update_item_by_id(user_id, user.model_dump(mode="json"))
    except Exception as e:
        return HttpResponse.internal_error(error=f"Unknown Error : {e}")

    return HttpResponse.success(response_data=classroom.model_dump(mode="json"))
