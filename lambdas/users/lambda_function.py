import logging
import os

import boto3
from create_user import create_user
from daftar_common.cognito_idp import CognitoIdentityProviderWrapper
from daftar_common.database_manager import TableManager
from daftar_common.http_response import HttpResponse
from delete_user_by_id import delete_user_by_id
from get_me import get_me
from get_user_by_id import get_user_by_id
from get_users import get_users
from update_user_by_id import update_user_by_id

# Initialisation du client DynamoDB
dynamodb = boto3.resource("dynamodb")
cognito_client = boto3.client("cognito-idp")

cognito_provider = CognitoIdentityProviderWrapper(
    cognito_idp_client=cognito_client,
    user_pool_id=os.environ["COGNITO_USER_POOL"],
    client_id=os.environ["COGNITO_CLIENT_ID"],
)

users_table_name = os.environ["DYNAMODB_USERS_TABLE_NAME"]
users_table = TableManager(dynamodb, table_name=users_table_name)

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    operation = event["httpMethod"]

    path_parameters = event.get("pathParameters")
    # headers = event.get("headers")
    resource = event.get("resource")

    access_token = event.get("headers", {}).get("Authorization")

    result = HttpResponse.not_found(error="Method Not found")

    if operation == "POST":
        try:
            result = create_user(event, cognito_provider, users_table)
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if operation == "GET":
        if resource == "/users/{id+}":
            user_id = path_parameters.get("id")
            try:
                result = get_user_by_id(users_table, user_id)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

        if resource == "/users":
            try:
                result = get_users(users_table)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

        if resource == "/me":
            try:
                result = get_me(users_table, access_token)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if operation == "DELETE":
        user_id = path_parameters.get("id")

        try:
            result = delete_user_by_id(users_table, cognito_provider, user_id)
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if operation == "PUT" and resource == "/users/{id+}":
        user_id = path_parameters.get("id")

        try:
            result = update_user_by_id(users_table, user_id, event)
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if operation == "OPTIONS":
        return HttpResponse.success(message="CORS Validated")

    return result
