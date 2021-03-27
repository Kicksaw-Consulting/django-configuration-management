import boto3
import base64
import json

from django_configuration_management.validation_utils import (
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


def parse_secret(secret_name: str, secret_keys: list) -> dict:
    secret_object = json.loads(get_secret(secret_name))
    secrets = dict()
    for secret_key in secret_keys:
        validate_key_name(secret_key)
        assert (
            secret_key in secret_object
        ), f"{secret_name} doesn't contain the key {secret_key}"
        secrets[secret_key] = secret_object[secret_key]
    return secrets


def pull_aws_config_data(data: dict):
    pulled = dict()
    for key, meta in data.items():
        secret_keys = meta["secret_keys"]

        assert (
            type(secret_keys) == list and len(secret_keys) > 0
        ), f"{key} must have a list of secret_keys"

        secret_object = parse_secret(key, secret_keys)
        pulled = {**pulled, **secret_object}
    return pulled
