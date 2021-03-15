import re


def validate_key_name(key_name: str):
    assert re.search(
        "^[A-Z0-9]+(?:_[A-Z0-9]+)*$", key_name
    ), f"Invalid key name {key_name}. Keys must consist only of uppercase letters and underscore"