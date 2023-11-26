
import boto3
import uuid
from datetime import datetime
import json
from decimal import Decimal
import os

from daftar_common.helper_functions import datetime_to_string, replace_decimals


class TableManager:


    def __init__(self, table_name):
        
        try:
            region = os.environ["AWS_REGION"]
        except IndexError:
            raise ValueError("AWS_REGION environment variable not set.")

        self.dynamo = boto3.resource('dynamodb', region)
        self.table = self.dynamo.Table(table_name)


        
    def add_item(self, item: dict):
        # UTC to ISO 8601 with Local TimeZone information without microsecond
        created_date = datetime_to_string(datetime.utcnow())
        item["createdDate"] = created_date

        item = json.loads(json.dumps(item), parse_float=Decimal)

        expected_dict = {'id': {"Exists": False}}

        self.table.put_item(Item=item, Expected=expected_dict)

        return True
