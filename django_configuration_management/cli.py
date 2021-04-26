import click
import os
import json

from django_configuration_management.aws_utils import pull_aws_config_data
from django_configuration_management.secrets import (
    decrypt_value,
    encrypt_value,
    generate_fernet_key,
)
from django_configuration_management.utils import gather_user_input, load_env
from django_configuration_management.github_script import (
    owner_and_repo,
    repository_info,
    encrypt_secret,
    push_secrets_to_github,
)
from django_configuration_management.yml_utils import dict_to_yml, yml_to_dict

from django_configuration_management.iam_script import configure_iam


@click.command("upsert_secret")
@click.option("-e", "--environment", default="development", help="Your environment")
def upsert_secret(environment):
    load_env(environment)

    data, _ = yml_to_dict(environment, skip_required_checks=True)
    key_name, key_value = gather_user_input()

    data[key_name] = {"value": key_value, "secret": True}

    dict_to_yml(data, environment)


@click.command("reveal_secrets")
@click.option("-e", "--environment", default="development", help="Your environment")
def reveal_secrets(environment):
    load_env(environment)

    local_secrets, aws_secrets = yml_to_dict(environment, skip_required_checks=True)

    for key, meta in local_secrets.items():
        # Skip non-secret values
        if type(meta) != dict:
            continue

        value = meta["value"]
        secret = decrypt_value(value)
        print(f"{key}={secret}")

    for key, secret in pull_aws_config_data(aws_secrets).items():
        print(f"{key}={secret}")


@click.command("generate_key")
def generate_key():
    key = generate_fernet_key()

    print(f"Your key is: \n\n{key}\n")
    print(
        "Please store this in whichever .env-[environment] file you generated it for under the variable ENC_KEY"
    )


@click.command("reencrypt")
@click.option("-e", "--environment", default="development", help="Your environment")
@click.option(
    "-k",
    "--new-key",
    help="The new key with which you'd like to re-encrypt your secrets",
)
def reencrypt(environment, new_key):
    load_env(environment)

    if not new_key:
        new_key = generate_fernet_key()

    data, _ = yml_to_dict(environment, skip_required_checks=True)

    for key, meta in data.items():
        # Skip non-secret values
        if type(meta) != dict:
            continue

        value = meta["value"]
        decrypted_value = decrypt_value(value)
        meta["value"] = encrypt_value(decrypted_value, enc_key=new_key)

        data[key] = meta

    dict_to_yml(data, environment)

    print(f"Your new key is: \n\n{new_key}\n")
    print(
        f"config-{environment}.yaml has been re-encrypted. Please be sure to update your .env-{environment} with the new key you used!"
    )


@click.command("github_secrets")
def github_secrets():
    """
    1. Get github public auth key from local env
    2. Get current repo name based on current dir
    3. Get repo public key
    4. Loop through `config-github.json` file and:
        - Ask to provide secret value for specific key
        - Encrypt provided secret
        - Save to dictionary
    5. Push secrets to github repo
    """
    print(
        "WARNING! This is an expiremental feature and is likely to change with future releases"
    )
    # check for the file right away
    with open(
        "config-github.json",
    ) as github_config_file:
        github_config = json.load(github_config_file)

    key = "GITHUB_ACCESS_TOKEN"
    github_access_token = os.getenv(key)

    assert github_access_token, f"Environment variable {key} not set"

    owner_repo_array = owner_and_repo()
    owner = owner_repo_array[0]
    repo_name = owner_repo_array[1]

    repo_key_info = repository_info(github_access_token, owner, repo_name)
    repo_key = repo_key_info[0]
    key_id = repo_key_info[1]

    user_provided_secrets = {}

    # Prompt user for secret and encrypt
    for key in github_config:
        prompt = f"Please provide the secret for key: {key}"
        repo_secret = input(prompt + " (or press enter to skip):\n")
        if not repo_secret:
            continue
        encrypted_secret = encrypt_secret(repo_key, repo_secret)
        user_provided_secrets[key] = encrypted_secret

    push_secrets_to_github(
        owner, repo_name, key_id, user_provided_secrets, github_access_token
    )


@click.command("iam_role")
def iam_role():
    print(
        "WARNING! This is an untested, expiremental feature. You use this at your own peril!"
    )
    configure_iam()
