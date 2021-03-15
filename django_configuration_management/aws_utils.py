import boto3
import base64
import json

from django_configuration_management.validation_utils import (
    read_required_vars_file,
    validate_key_name,
)


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
    _check_aws_required_keys(secret_object, secret_name)
    return secret_object


def _check_aws_required_keys(secret_object: dict, secret_name: str):
    required_vars = read_required_vars_file()
    if not required_vars:
        return

    missing_keys = []
    for key in required_vars.pop("aws_secrets"):
        if key not in secret_object:
            missing_keys.append(key)

    assert (
        len(missing_keys) < 1
    ), f"The following keys are required in AWS Secret Manager for {secret_name}. {missing_keys}. Halting"