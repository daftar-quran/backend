from daftar_common.http_response import HttpResponse
from daftar_common.models.users import User
from pydantic import ValidationError


def delete_user_by_id(users_table, cognito_client, user_id):

    # TODO: Check that user is admin (= has permissions to remove a user)
    result = users_table.get_item_by_id(user_id)
    if not result:
        return HttpResponse.not_found(error="User not found")

    try:
        user = User(**result)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Internal validation Error : {e}")

    # Delete on Cognito
    try:
        cognito_client.delete_user_by_username(user.pseudo)
    except Exception as e:
        return HttpResponse.internal_error(error=f"Unknown Error : {e}")

    # Delete on DB
    try:
        users_table.delete_item_by_id(user_id)
    except ValidationError as e:
        return HttpResponse.internal_error(error=f"Unknown error : {e}")

    return HttpResponse.success(message="User deleted successfully.")
