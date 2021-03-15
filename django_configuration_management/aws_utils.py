import boto3
import base64
import json

from django_configuration_management.validation_utils import validate_key_name
from django_configuration_management.yml_utils import check_aws_required_keys


def get_secret(secret_name):
    client = boto3.client("secretsmanager")

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in get_secret_value_response:
        secret = get_secret_value_response["SecretString"]
    else:
        secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    return secret


def parse_secret(secret_name: str) -> dict:
    secret_object = json.loads(get_secret(secret_name))
    for secret_key in secret_object:
        validate_key_name(secret_key)
    check_aws_required_keys(secret_object, secret_name)
    return secret_object
