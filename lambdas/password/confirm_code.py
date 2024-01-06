import json

from daftar_common.http_response import HttpResponse
from pydantic import BaseModel, ValidationError


class ConfirmCodePayload(BaseModel):
    user_id: str
    confirmation_code: str
    new_password: str


def confirm_code(event, cognito_provider):

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
        confirm_code = ConfirmCodePayload(**payload)
    except ValidationError as err:
        return HttpResponse.bad_request(error=err.errors())

    user_id = confirm_code.user_id
    confirmation_code = confirm_code.confirmation_code
    new_password = confirm_code.new_password

    try:
        cognito_provider.confirm_forgot_password(user_id, confirmation_code, new_password)
    except Exception as e:
        return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    return HttpResponse.success(message="Success")
