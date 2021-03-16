from django.conf import settings

from django_configuration_management.aws_utils import pull_aws_config_data
from django_configuration_management.utils import (
    load_env,
    normalize_config_data,
)
from django_configuration_management.yml_utils import yml_to_dict


def get_config(environment: str, dotenv_required=True):
    try:
        load_env(environment)
    except AssertionError as error:
        if dotenv_required:
            raise error

    local_secrets, aws_secrets = yml_to_dict(environment)

    normalized_local_secrets = normalize_config_data(local_secrets)
    pulled_aws_secrets = pull_aws_config_data(aws_secrets)

    return {**normalized_local_secrets, **pulled_aws_secrets}


def inject_config(environment: str, settings_module: settings, dotenv_required=True):
    config = get_config(environment, dotenv_required)

    for key, value in config.items():
        setattr(settings_module, key, value)
