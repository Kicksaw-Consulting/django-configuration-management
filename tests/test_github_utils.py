import pytest

from django_configuration_management.github_utils import owner_and_repo

import django_configuration_management.github_utils as github_utils_module


@pytest.mark.parametrize(
    "url,owner,repo",
    [
        # HTTPS
        (
            "https://github.com/brno32/django-configuration-management.git",
            "brno32",
            "django-configuration-management",
        ),
        # SSH
        (
            "git@github.com:brno32/django-configuration-management.git",
            "brno32",
            "django-configuration-management",
        ),
        # check patterns
        (
            "https://github.com/Kicksaw-Consulting/notify-slack-action.git",
            "Kicksaw-Consulting",
            "notify-slack-action",
        ),
        (
            "https://github.com/Kicksaw_Consulting/notify_slack_action.git",
            "Kicksaw_Consulting",
            "notify_slack_action",
        ),
    ],
)
def test_owner_and_repo(monkeypatch, url, owner, repo):
    monkeypatch.setattr(github_utils_module, "get_remote_repo", lambda *args: url)

    results = owner_and_repo()

    parsed_owner = results[0]
    parsed_repo = results[1]

    assert parsed_owner == owner
    assert parsed_repo == repo
