import json
import os
import boto3

from daftar_common.models.users import UserSchema
from daftar_common.http_response import HttpResponse
from daftar_common.database_manager import TableManager

from marshmallow import ValidationError

# Initialisation du client DynamoDB
dynamodb = boto3.resource('dynamodb')

users_table_name = os.environ['DYNAMODB_USERS_TABLE_NAME']

users_table = TableManager(dynamodb, table_name=users_table_name)


def lambda_handler(event, context):
    operation = event['httpMethod']
    endpoint = event.get('resource')
    path_parameters = event.get('pathParameters')
    headers = event.get('headers')
        
    if operation == "POST":

        try:
            payload = None
            body = event.get('body')
            if body:
                payload = json.loads(body)
        except Exception as e:
            print(e)
            return HttpResponse.bad_request(error="Could not decode JSON body")

        # Data Validation
        try:
            user_schema = UserSchema()
            user = user_schema.load(payload)
        except ValidationError as err:
            return HttpResponse.bad_request(error=err.messages)

        # Check that user does not exist
        # TODO


        try:
            users_table.add_item(item=user_schema.dump(user))
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")


        return HttpResponse.success(response_data=user_schema.dump(user))
