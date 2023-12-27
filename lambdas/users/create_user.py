import datetime
import json
import uuid
from typing import Optional

from daftar_common.http_response import HttpResponse
from daftar_common.models.users import User
from pydantic import BaseModel, EmailStr, ValidationError


class UserSignup(BaseModel):
    pseudo: str
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    birthdate: datetime.date
    address: Optional[str] = ""


def create_user(event, cognito_provider, users_table):

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
        user_signup = UserSignup(**payload)
    except ValidationError as err:
        return HttpResponse.bad_request(error=err.errors())

    user = User(**user_signup.model_dump(exclude=("password")))

    # Check that user does not exist
    # TODO

    resp_cognito = {}
    try:
        resp_cognito, already_exists = cognito_provider.sign_up_user(
            user_name=user.pseudo, password=payload["password"], user_email=user.email
        )
    except Exception as e:
        return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if already_exists:
        return HttpResponse.bad_request(
            error=f"User already exists and confirmed. : {resp_cognito}"
        )
    # print(resp_cognito)
    is_unconfirmed = resp_cognito.get("UserStatus") == "UNCONFIRMED"

    if is_unconfirmed:
        return HttpResponse.bad_request(
            error=f"User already exists and is unconfirmed. Please confirm email : {resp_cognito}"
        )

    cognito_sub_id = resp_cognito["UserSub"]
    user.id = uuid.UUID(cognito_sub_id)

    try:
        users_table.add_item(item=user.model_dump(mode="json"))
    except Exception as e:
        return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    return HttpResponse.success(response_data=user.model_dump(mode="json"))
