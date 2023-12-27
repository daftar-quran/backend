from daftar_common.http_response import HttpResponse
from daftar_common.models.users import User
from pydantic import ValidationError


def get_user_by_id(users_table, user_id):

    result = users_table.get_item_by_id(user_id)
    if not result:
        return HttpResponse.not_found(error="User not found")

    try:
        user = User(**result)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")
    return HttpResponse.success(response_data=user.model_dump(mode="json"))
