from django.conf import settings

from django_configuration_management.utils import load_env, normalize_config_data
from django_configuration_management.yml_utils import yml_to_dict


def get_config(environment: str, dotenv_required=True):
    try:
        load_env(environment)
    except AssertionError as error:
        if dotenv_required:
            raise error

    data = yml_to_dict(environment)

    return normalize_config_data(data)


def inject_config(environment: str, settings_module: settings, dotenv_required=True):
    config = get_config(environment, dotenv_required)

    for key, value in config.items():
        setattr(settings_module, key, value)
