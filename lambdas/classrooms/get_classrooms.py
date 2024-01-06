import uuid
from typing import List

from daftar_common.http_response import HttpResponse
from pydantic import BaseModel, Field, ValidationError


class TinyClassroom(BaseModel, validate_assignment=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    tikrar_goal: int


class TinyClassrooms(BaseModel):
    classrooms: List[TinyClassroom]


def get_classrooms(classrooms_table):

    result = classrooms_table.scan_table()
    try:
        classrooms = TinyClassrooms(classrooms=result)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")
    return HttpResponse.success(response_data=classrooms.model_dump(mode="json"))
