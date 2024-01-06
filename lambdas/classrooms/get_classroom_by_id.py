from daftar_common.http_response import HttpResponse
from daftar_common.models.classrooms import Classroom
from pydantic import ValidationError


def get_classroom_by_id(classrooms_table, classroom_id):

    result = classrooms_table.get_item_by_id(classroom_id)
    if not result:
        return HttpResponse.not_found(error="Classroom not found")

    try:
        classroom = Classroom(**result)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")
    return HttpResponse.success(response_data=classroom.model_dump(mode="json"))
