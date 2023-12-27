import json
import uuid
from daftar_common.models.users import User
from daftar_common.http_response import HttpResponse
from pydantic import ValidationError


def update_user_by_id(users_table, user_id, event):

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
        user = User(**payload)
    except ValidationError as err:
        return HttpResponse.bad_request(error=err.errors())

    user_exists = users_table.get_item_by_id(user_id)
    if not user_exists:
        return HttpResponse.not_found(error="User not found")
    user_db = User(**user_exists)

    # prevent email + username update
    if user_db.pseudo != user.pseudo:
        return HttpResponse.bad_request(error="Cannot update username for now")
    if user_db.email != user.email:
        return HttpResponse.bad_request(error="Cannot update email for now")

    user.id = uuid.UUID(user_id)
    try:
        updated = users_table.update_item_by_id(user_id, user.model_dump(mode='json'))
    except Exception as e:
        return HttpResponse.internal_error(error=f"Unknown Error : {e}")

    if not updated:
        return HttpResponse.internal_error(error="Unknown Error")

    return HttpResponse.success(response_data=user.model_dump(mode='json'))

    