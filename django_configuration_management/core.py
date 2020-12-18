import os

from django.conf import settings

from django_configuration_management.utils import load_env, normalize_config_data
from django_configuration_management.yml_utils import yml_to_dict


def get_config(environment: str, skip_dotenv_load=False):
    if not skip_dotenv_load:
        load_env(environment)

    data = yml_to_dict(environment)

    return normalize_config_data(data)


def inject_config(environment: str, settings_module: settings, skip_dotenv_load=False):
    config = get_config(environment, skip_dotenv_load)

    for key, value in config.items():
        setattr(settings_module, key, value)
