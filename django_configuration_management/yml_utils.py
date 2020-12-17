import re

import yaml


def _validate_yml(data):
    for key, meta in data.items():
        validate_key_name(key)
        assert (
            type(meta.get("secret")) == bool
        ), f"{key} has an invalid row. Missing 'secret'"
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
