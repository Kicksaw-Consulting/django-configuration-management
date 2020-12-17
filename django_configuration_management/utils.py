import os
from getpass import getpass
from pathlib import Path

from dotenv import load_dotenv

from django_configuration_management.secrets import encrypt_value
from django_configuration_management.yml_utils import validate_key_name


def load_env(environment):
    env_path = Path(".") / f".env-{environment}"
    if os.path.isfile(env_path):
        load_dotenv(dotenv_path=env_path, verbose=True)
        return

    print(
        f"env not found: {env_path}. This file is required and must contain your ENC_KEY"
    )
    exit(1)


def gather_user_input():
    key_name = input("Enter key name: ")

    validate_key_name(key_name)

    key_value = getpass("Enter key value: ")

    return key_name, encrypt_value(key_value)
