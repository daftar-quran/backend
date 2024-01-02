from daftar_common.http_response import HttpResponse
from daftar_common.models.classrooms import Classroom
from pydantic import ValidationError


def delete_classroom_by_id(classrooms_table, classroom_id):

    # TODO: Check that classroom is admin (= has permissions to remove a classroom)
    result = classrooms_table.get_item_by_id(classroom_id)
    if not result:
        return HttpResponse.not_found(error="Classroom not found")

    try:
        Classroom(**result)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")

    # Delete on DB
    try:
        classrooms_table.delete_item_by_id(classroom_id)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Unknown error : {e}")

    return HttpResponse.success(message="Classroom deleted successfully.")
