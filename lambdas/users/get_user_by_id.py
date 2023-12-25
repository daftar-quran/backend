from pydantic import ValidationError
from daftar_common.http_response import HttpResponse
from daftar_common.models.users import User


def get_user_by_id(users_table, id_user):
    
    result = users_table.get_item_by_id(id_user)
    if not result:
        return HttpResponse.not_found(error="User not found")

    try:
        user = User(**result)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")
    return HttpResponse.success(response_data=user.model_dump(mode='json'))
