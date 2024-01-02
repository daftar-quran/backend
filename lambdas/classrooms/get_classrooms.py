from daftar_common.http_response import HttpResponse
from daftar_common.models.classrooms import Classrooms
from pydantic import ValidationError


def get_classrooms(classrooms_table):

    result = classrooms_table.scan_table()
    try:
        classrooms = Classrooms(classrooms=result)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")
    return HttpResponse.success(response_data=classrooms.model_dump(mode="json"))
