

import json

from typing import Optional
import uuid
import datetime
from daftar_common.models.users import User
from daftar_common.http_response import HttpResponse

from pydantic import BaseModel, Field, EmailStr, ValidationError



class UserSignup(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
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
    password = user_signup.password

    user = User(**user_signup.model_dump(exclude=('password')))

    # Check that user does not exist
    # TODO
    
    resp_cognito = {}
    try:
        resp_cognito, already_exists = cognito_provider.sign_up_user(user_name=user.pseudo, password=payload['password'], user_email=user.email)
    except Exception as e:
        return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if already_exists:
        return HttpResponse.bad_request(error=f"User already exists and confirmed. : {resp_cognito}")
    # print(resp_cognito)
    is_unconfirmed = resp_cognito.get('UserStatus') == 'UNCONFIRMED'
    
    if is_unconfirmed:
        return HttpResponse.bad_request(error=f"User already exists and is unconfirmed. Please confirm email : {resp_cognito}")
    
    # TODO: add user Cognito sub ID
    # cognito_sub_id = next(filter(lambda d: d['Name'] == 'sub', resp_cognito['UserAttributes']), {}).get('Value', None)
    cognito_sub_id = resp_cognito['UserSub']
    user.id = uuid.UUID(cognito_sub_id)

    try:
        users_table.add_item(item=user.model_dump(mode='json'))
    except Exception as e:
        return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    return HttpResponse.success(response_data=user_signup.model_dump(mode='json'))
