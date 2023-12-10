

import json

from typing import List, Optional
import uuid
import datetime
from daftar_common.models.users import User

from pydantic import BaseModel, Field, EmailStr, ValidationError
from daftar_common.http_response import HttpResponse

from daftar_common.cognito_idp import CognitoIdentityProviderWrapper


class UserSignup(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    pseudo: str
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    is_admin: bool
    birthdate: datetime.date
    address: Optional[str] = ""


def create_user(event, cognito_client, users_table):

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
    

    cpw = CognitoIdentityProviderWrapper(
        cognito_idp_client=cognito_client, 
        user_pool_id="eu-west-1_p7iXXgN8f", 
        client_id="rvkim25uu2nbvo5prfuucmfn5")
    
    resp_cognito = {}
    try:
        resp_cognito, already_exists = cpw.sign_up_user(user_name=user.pseudo, password=payload['password'], user_email=user.email)
    except Exception as e:
        return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if already_exists:
        return HttpResponse.bad_request(error=f"User already exists and confirmed. : {resp_cognito}")
    
    is_unconfirmed = resp_cognito['UserStatus'] == 'UNCONFIRMED'
    
    if is_unconfirmed:
        return HttpResponse.bad_request(error=f"User already exists and is unconfirmed. Please confirm email : {resp_cognito}")
    
    # TODO: add user Cognito sub ID
    cognito_sub_id = next(filter(lambda d: d['Name'] == 'sub', resp_cognito['UserAttributes']), {}).get('Value', None)
    # user.cognito_id = cognito_sub_id
    
    try:
        users_table.add_item(item=user.model_dump(mode='json'))
    except Exception as e:
        return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    return HttpResponse.success(response_data=user_signup.model_dump())