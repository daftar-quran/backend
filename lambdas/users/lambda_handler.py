import json
import os
import uuid
import boto3
import logging

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr, ValidationError

from daftar_common.models.users import User
from daftar_common.http_response import HttpResponse
from daftar_common.database_manager import TableManager
from daftar_common.cognito_idp import CognitoIdentityProviderWrapper


# Initialisation du client DynamoDB
dynamodb = boto3.resource("dynamodb")
cognito_client = boto3.client('cognito-idp')
users_table_name = os.environ["DYNAMODB_USERS_TABLE_NAME"]
users_table = TableManager(dynamodb, table_name=users_table_name)

logger = logging.getLogger(__name__)



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


def lambda_handler(event, context):
    operation = event["httpMethod"]
    endpoint = event.get("resource")
    path_parameters = event.get("pathParameters")
    headers = event.get("headers")

    if operation == "POST":
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
        
        signup_confirmed = False
        resp_cognito = {}
        try:
            resp_cognito, already_exists = cpw.sign_up_user(user_name=user.pseudo, password=payload['password'], user_email=user.email)
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

        if already_exists:
            return HttpResponse.bad_request(error=f"User already exists and confirmed. : {resp_cognito}")

        try:
            users_table.add_item(item=user_signup.model_dump())
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

        return HttpResponse.success(response_data=user_signup.model_dump())
