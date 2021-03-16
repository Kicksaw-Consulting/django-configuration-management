from django_configuration_management.aws_utils import pull_aws_config_data

import django_configuration_management.aws_utils as aws_utils_module


def test_pull_aws_config_data(monkeypatch):
    monkeypatch.setattr(
        aws_utils_module, "parse_secret", lambda *args: {"AWS_SECRET": "im a secret"}
    )
    fake_data = {
        "some/path/to/secret": {
            "secret_keys": ["AWS_SECRET"],
            "secret_keys": ["AWS_SECRET"],
        }
    }
    pulled = pull_aws_config_data(fake_data)

    assert pulled == {"AWS_SECRET": "im a secret"}
