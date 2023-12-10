import json
import os
import boto3
import logging


from daftar_common.http_response import HttpResponse
from daftar_common.database_manager import TableManager
from create_user import create_user

# Initialisation du client DynamoDB
dynamodb = boto3.resource("dynamodb")
cognito_client = boto3.client('cognito-idp')
users_table_name = os.environ["DYNAMODB_USERS_TABLE_NAME"]
users_table = TableManager(dynamodb, table_name=users_table_name)

logger = logging.getLogger(__name__)





def lambda_handler(event, context):
    operation = event["httpMethod"]
    endpoint = event.get("resource")
    path_parameters = event.get("pathParameters")
    headers = event.get("headers")

    if operation == "POST":
        
        try:
            result = create_user(event, cognito_client, users_table)
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")
