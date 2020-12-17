import re

import yaml


def _validate_yml(data):
    for key, meta in data.items():
        validate_key_name(key)

        if type(meta) == dict:
            secret = meta.get("secret")
            assert type(secret) == bool, f"{key} has an invalid row. Missing 'secret'"
            assert (
                secret
            ), f"{key} is structured like a secret value, but you've marked it as 'secret: false'. The value of this key can simply be the plain text value."
            assert (
                type(meta.get("value")) == str
            ), f"{key} has an invalid row. Missing 'value'"


def yml_to_dict(environment: str):
    try:
        with open(f"{environment}-config.yaml", "r") as yml:
            loaded: dict = yaml.safe_load(yml)
    except FileNotFoundError:
        loaded = {}

    _validate_yml(loaded)
    return loaded


def dict_to_yml(data: dict, environment: str) -> str:
    with open(f"{environment}-config.yaml", "w+") as yml:
        dumped = yaml.dump(data, yml)
    return dumped


def validate_key_name(key_name: str):
    assert re.search(
        "^[A-Z]+(?:_[A-Z]+)*$", key_name
    ), f"Invalid key name {key_name}. Keys must consist only of uppercase letters and underscore"
