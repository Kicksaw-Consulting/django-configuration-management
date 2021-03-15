import json
import yaml

from pathlib import Path

from django_configuration_management.validation_utils import validate_key_name


def _validate_yml(data, skip_required_checks=False):
    if not skip_required_checks:
        _check_required_keys(data)

    for key, meta in data.items():
        if type(meta) == dict:
            secret = meta.get("secret")
            use_aws = meta.get("use_aws")
            if secret is not None:
                validate_key_name(key)
                assert (
                    secret
                ), f"{key} is structured like a secret value, but you've marked it as 'secret: false'. The value of this key can simply be the plain text value."
                assert (
                    type(meta.get("value")) == str
                ), f"{key} has an invalid row. Missing 'value'"
            elif use_aws is not None:
                assert (
                    use_aws
                ), f"{key} is structured like its value comes from AWS Secret Manager, but it's been marked as 'use_aws: false'. This value of this key can simply be the plain text value."
            else:
                raise AssertionError(f"{key} has an invalid row. Missing 'secret_name'")
        else:
            validate_key_name(key)


def _check_required_keys(data):
    required_vars = Path(".") / "config-required.json"

    try:
        with open(required_vars, "r") as file:
            required_vars = json.load(file)
    except FileNotFoundError:
        return

    missing_keys = []
    for key in required_vars:
        if key == "aws_secrets":
            pass
        elif key not in data:
            missing_keys.append(key)

    assert (
        len(missing_keys) < 1
    ), f"The following keys are required. {missing_keys}. Halting"


def check_aws_required_keys(secret_object: dict, secret_name: str):
    required_vars = Path(".") / "config-required.json"

    try:
        with open(required_vars, "r") as file:
            required_vars = json.load(file)
    except FileNotFoundError:
        return

    missing_keys = []
    for key in required_vars.pop("aws_secrets"):
        if key not in secret_object:
            missing_keys.append(key)

    assert (
        len(missing_keys) < 1
    ), f"The following keys are required in AWS Secret Manager for {secret_name}. {missing_keys}. Halting"


def yml_to_dict(environment: str, skip_required_checks=False):
    try:
        with open(f"config-{environment}.yaml", "r") as yml:
            loaded: dict = yaml.safe_load(yml)
    except FileNotFoundError:
        loaded = {}

    _validate_yml(loaded, skip_required_checks)
    return loaded


def dict_to_yml(data: dict, environment: str) -> str:
    with open(f"config-{environment}.yaml", "w+") as yml:
        dumped = yaml.dump(data, yml)
    return dumped
