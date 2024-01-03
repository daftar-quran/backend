import logging
import os

import boto3
from create_classroom import create_classroom
from daftar_common.database_manager import TableManager
from daftar_common.http_response import HttpResponse
from delete_classroom_by_id import delete_classroom_by_id
from get_classroom_by_id import get_classroom_by_id
from get_classrooms import get_classrooms
from switch_roles import switch_roles

# Initialisation du client DynamoDB
dynamodb = boto3.resource("dynamodb")

classrooms_table_name = os.environ["DYNAMODB_CLASSROOMS_TABLE_NAME"]
classrooms_table = TableManager(dynamodb, table_name=classrooms_table_name)

users_table_name = os.environ["DYNAMODB_USERS_TABLE_NAME"]
users_table = TableManager(dynamodb, table_name=users_table_name)

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    operation = event["httpMethod"]

    path_parameters = event.get("pathParameters")
    # headers = event.get("headers")
    resource = event.get("resource")

    classroom_id = path_parameters.get("id")
    result = HttpResponse.not_found(error="Method Not found")

    if operation == "POST":
        if resource == "/classrooms":
            try:
                result = create_classroom(event, users_table, classrooms_table)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")
        if resource == "/classrooms/{id}/switchRole":
            try:
                result = switch_roles(
                    event, classroom_id, users_table, classrooms_table
                )
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")
    if operation == "GET":
        if resource == "/classrooms/{id}":
            try:
                result = get_classroom_by_id(classrooms_table, classroom_id)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

        if resource == "/classrooms":
            try:
                result = get_classrooms(classrooms_table)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if operation == "DELETE":
        classroom_id = path_parameters.get("id")

        try:
            result = delete_classroom_by_id(classrooms_table, classroom_id)
        except Exception as e:
            return HttpResponse.internal_error(error=f"Internal Server Error : {e}")

    if operation == "PUT" and resource == "/classrooms/{id+}":
        # No PUT operation
        pass

    if operation == "OPTIONS":
        return HttpResponse.success(message="CORS Validated")

    return result
