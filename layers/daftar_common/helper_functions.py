import decimal
from datetime import datetime
import json

DATE_FORMAT = "%Y-%m-%d"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def replace_decimals(obj):
    # https://github.com/boto/boto3/issues/369

    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj:
            obj[k] = replace_decimals(obj[k])
        return obj

    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(CustomJsonEncoder, self).default(o)


def datetime_to_string(datetime_object):
    return datetime_object.strftime(DATE_TIME_FORMAT)


def date_to_string(date_object):
    return date_object.strftime(DATE_FORMAT)


def string_to_date(str_date_object):
    return datetime.strptime(str_date_object, DATE_FORMAT).date()


def string_to_datetime(str_datetime_object):
    return datetime.strptime(str_datetime_object, DATE_TIME_FORMAT)
