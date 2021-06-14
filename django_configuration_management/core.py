import os
from typing import Callable
import django

from django.conf import settings

from django_configuration_management.aws_utils import pull_aws_config_data
from django_configuration_management.utils import (
    load_env,
    normalize_config_data,
)
from django_configuration_management.yml_utils import yml_to_dict


def get_config(environment: str, dotenv_required=True, region_name=None):
    try:
        load_env(environment)
    except AssertionError as error:
        if dotenv_required:
            raise error

    local_secrets, aws_secrets = yml_to_dict(environment)

    normalized_local_secrets = normalize_config_data(local_secrets)
    pulled_aws_secrets = pull_aws_config_data(aws_secrets, region_name=region_name)

    return {**normalized_local_secrets, **pulled_aws_secrets}


def inject_config(
    environment: str, settings_module: settings, dotenv_required=True, region_name=None
):
    config = get_config(
        environment, dotenv_required=dotenv_required, region_name=region_name
    )

    for key, value in config.items():
        setattr(settings_module, key, value)


def load_django(
    path_to_settings_module: str,
    pre_setup_hook: Callable = lambda *args, **kwargs: ...,
    pre_setup_hook_args: list = [],
    pre_setup_hook_kwargs: dict = {},
    post_setup_hook: Callable = lambda *args, **kwargs: ...,
    post_setup_hook_args: list = [],
    post_setup_hook_kwargs: dict = {},
):
    """
    For use in scripts that are invoked via manage.py, e.g., lambda environments, non-management command CLI scripts, etc
    """
    pre_setup_hook(*pre_setup_hook_args, **pre_setup_hook_kwargs)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", path_to_settings_module)
    django.setup()
    post_setup_hook(*post_setup_hook_args, **post_setup_hook_kwargs)