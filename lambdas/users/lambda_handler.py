import json
import os
import uuid
import boto3
import logging
from marshmallow import ValidationError, fields, Schema, post_load

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


class UserSignupSchema(Schema):
    id = fields.UUID(load_default=uuid.uuid4)
    pseudo = fields.Str(required=True)  # TODO: Do not allow special char, space etc.
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Email(required=True)
    is_admin = fields.Boolean(required=True)
    birthdate = fields.Date(required=True)
    address = fields.Str()

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


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
            user_schema = UserSignupSchema()
            user = user_schema.load(payload)
        except ValidationError as err:
            return HttpResponse.bad_request(error=err.messages)

        # Check that user does not exist
        # TODO

        cpw = CognitoIdentityProviderWrapper(
            cognito_idp_client=cognito_client,
            user_pool_id="eu-west-1_p7iXXgN8f",
            client_id="rvkim25uu2nbvo5prfuucmfn5")

        signup_confirmed = False
        resp_cognito = {}
        try:
            resp_cognito, already_exists = cpw.sign_up_user(user_name=user.pseudo, password=payload['password'],
                                                            user_email=user.email)
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

        if already_exists:
            return HttpResponse.bad_request(error=f"User already exists and confirmed. : {resp_cognito}")

        try:
            users_table.add_item(item=user_schema.dump(user))
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

        return HttpResponse.success(response_data=user_schema.dump(user))
