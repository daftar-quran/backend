import json
import os
import boto3
import logging


from daftar_common.http_response import HttpResponse
from daftar_common.database_manager import TableManager
from create_user import create_user
from get_user_by_id import get_user_by_id
from delete_user_by_id import delete_user_by_id
from get_users import get_users
from get_me import get_me
from daftar_common.cognito_idp import CognitoIdentityProviderWrapper

# Initialisation du client DynamoDB
dynamodb = boto3.resource("dynamodb")
cognito_client = boto3.client('cognito-idp')

cognito_provider = CognitoIdentityProviderWrapper(
    cognito_idp_client=cognito_client, 
    user_pool_id="eu-west-1_p7iXXgN8f", 
    client_id="rvkim25uu2nbvo5prfuucmfn5")

users_table_name = os.environ["DYNAMODB_USERS_TABLE_NAME"]
users_table = TableManager(dynamodb, table_name=users_table_name)

logger = logging.getLogger(__name__)





def lambda_handler(event, context):
    operation = event["httpMethod"]
    endpoint = event.get("resource")
    path_parameters = event.get("pathParameters")
    headers = event.get("headers")
    resource = event.get("resource")

    access_token = event.get('headers', {}).get('Authorization')

    if operation == "POST":
        
        try:
            result = create_user(event, cognito_provider, users_table)
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if operation == "GET":
        if resource == "/users/{id+}":
            id_user = path_parameters.get('id')
            try:
                result = get_user_by_id(users_table, id_user)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

        if resource == "/users":
            try:
                result = get_users(users_table)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

        if resource == "/users/me":
            try:
                result = get_me(users_table, cognito_provider, access_token)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")
           

    if operation == "DELETE":
        id_user = path_parameters.get('id')
        
        try:
            result = delete_user_by_id(users_table, cognito_provider, id_user)
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")
    


    return result