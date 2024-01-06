import logging
import os

import boto3
from confirm_code import confirm_code
from daftar_common.cognito_idp import CognitoIdentityProviderWrapper
from daftar_common.http_response import HttpResponse
from forgot_password import forgot_password

cognito_client = boto3.client("cognito-idp")


cognito_provider = CognitoIdentityProviderWrapper(
    cognito_idp_client=cognito_client,
    user_pool_id=os.environ["COGNITO_USER_POOL"],
    client_id=os.environ["COGNITO_CLIENT_ID"],
)

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    operation = event["httpMethod"]

    path_parameters = event.get("pathParameters", {})
    if not path_parameters:
        path_parameters = {}
    # headers = event.get("headers")
    resource = event.get("resource")

    result = HttpResponse.not_found(error="Method Not found")

    if operation == "POST":
        if resource == "/passwords/forgot":
            try:
                result = forgot_password(event, cognito_provider)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")
        if resource == "/passwords/confirmCode":
            try:
                result = confirm_code(event)
            except Exception as e:
                return HttpResponse.internal_error(error=f"Internal Server Error : {e}")
    if operation == "OPTIONS":
        return HttpResponse.success(message="CORS Validated")

    return result
