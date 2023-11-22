import json
import os
import boto3

from daftar_common.models.users import User, UserSchema

from http_response import HttpResponse
from marshmallow import ValidationError

# Initialisation du client DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_TABLE_NAME']
table = dynamodb.Table(table_name)


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

        try:
            table.put_item(Item=user_schema.dump(user))
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")


        return HttpResponse.success(response_data=user_schema.dump(user))
