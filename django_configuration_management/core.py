from django.conf import settings

from django_configuration_management.utils import load_env, normalize_config_data
from yml_utils import yml_to_dict


def get_config(environment: str):
    load_env(environment)

    data = yml_to_dict(environment)

    return normalize_config_data(data)


def inject_config(environment: str, settings_module: settings):
    config = get_config(environment)

    for key, value in config.items():
        setattr(settings_module, key, value)
