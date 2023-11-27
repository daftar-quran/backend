import boto3
import uuid
from datetime import datetime
import json
from decimal import Decimal
import os

from daftar_common.helper_functions import datetime_to_string, replace_decimals


class TableManager:
    def __init__(self, dynamo_resource, table_name):
        self.dynamo = dynamo_resource
        self.table = self.dynamo.Table(table_name)

    def add_item(self, item: dict):
        # UTC to ISO 8601 with Local TimeZone information without microsecond
        created_date = datetime_to_string(datetime.utcnow())
        item["createdDate"] = created_date

        item = json.loads(json.dumps(item), parse_float=Decimal)

        expected_dict = {"id": {"Exists": False}}

        self.table.put_item(Item=item, Expected=expected_dict)

        return True
