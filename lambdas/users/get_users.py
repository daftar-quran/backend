from pydantic import ValidationError

from daftar_common.http_response import HttpResponse
from daftar_common.models.users import Users


def get_users(users_table):

    result = users_table.scan_table()
    try:
        users = Users(users=result)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")
    return HttpResponse.success(response_data=users.model_dump(mode='json'))
