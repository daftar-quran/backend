import json

from daftar_common.http_response import HttpResponse
from daftar_common.models.classrooms import Classroom
from pydantic import BaseModel, ValidationError


class ClassroomCreation(BaseModel):
    name: str
    tikrar_goal: str


def create_classroom(event, classrooms_table):

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
        classroom_init = ClassroomCreation(**payload)
    except ValidationError as err:
        return HttpResponse.bad_request(error=err.errors())

    classroom = Classroom(**classroom_init.model_dump())

    try:
        classrooms_table.add_item(item=classroom.model_dump(mode="json"))
    except Exception as e:
        return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    return HttpResponse.success(response_data=classroom.model_dump(mode="json"))
