import json

from daftar_common.http_response import HttpResponse
from pydantic import BaseModel, ValidationError


class ForgotPasswordPayload(BaseModel):
    user_id: str


def forgot_password(event, cognito_provider):

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
        forgot_password = ForgotPasswordPayload(**payload)
    except ValidationError as err:
        return HttpResponse.bad_request(error=err.errors())

    user_id = forgot_password.user_id

    try:
        cognito_provider.forgot_password(user_id)
    except Exception as e:
        return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    return HttpResponse.success(message="Success")
