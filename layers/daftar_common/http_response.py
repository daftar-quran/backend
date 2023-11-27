import json


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(CustomJsonEncoder, self).default(o)


class HttpResponse:
    @classmethod
    def _generic_response(cls, response_data, message, error, status):
        response = dict()
        if response_data:
            response["data"] = response_data
        if message:
            response["message"] = message
        if error:
            response["error"] = error

        return {
            "body": json.dumps(response, cls=CustomJsonEncoder),
            "statusCode": status,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
            },
        }

    @classmethod
    def success(cls, response_data=[], message=None, error=None):
        return cls._generic_response(
            response_data, message=message, error=error, status=200
        )

    @classmethod
    def not_found(cls, response_data=[], message=None, error=None):
        return cls._generic_response(
            response_data, message=message, error=error, status=404
        )

    @classmethod
    def bad_request(cls, response_data=[], message=None, error=None):
        return cls._generic_response(
            response_data, message=message, error=error, status=400
        )

    @classmethod
    def unauthorized(cls, response_data=[], message=None, error=None):
        return cls._generic_response(
            response_data, message=message, error=error, status=401
        )

    @classmethod
    def conflict(cls, response_data=[], message=None, error=None):
        return cls._generic_response(
            response_data, message=message, error=error, status=409
        )

    @classmethod
    def internal_error(cls, response_data=[], message=None, error=None):
        return cls._generic_response(
            response_data, message=message, error=error, status=500
        )
