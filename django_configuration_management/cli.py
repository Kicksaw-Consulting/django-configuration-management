import click

from django_configuration_management.secrets import decrypt_value, generate_fernet_key
from django_configuration_management.utils import gather_user_input, load_env
from django_configuration_management.yml_utils import dict_to_yml, yml_to_dict


@click.command("upsert_secret")
@click.option("--environment", default="development", help="Your environment")
def upsert_secret(environment):
    load_env(environment)

    data = yml_to_dict(environment)
    key_name, key_value = gather_user_input()

    data[key_name] = {"value": key_value, "secret": True}

    print(data)

    dict_to_yml(data, environment)


@click.command("reveal_secrets")
@click.option("--environment", default="development", help="Your environment")
def reveal_secrets(environment):
    load_env(environment)

    data = yml_to_dict(environment)

    for key, desc in data.items():
        is_secret = desc.get("secret")

        if not is_secret:
            continue

        value = desc["value"]
        decrypted_value = decrypt_value(value)

        print(f"{key}={decrypted_value}")


@click.command("generate_key")
def generate_key():
    key = generate_fernet_key()

    print(f"Your key is: \n\n{key}\n")
    print(
        "Please store this in whichever .env-[environment] file you generated it for under the variable ENC_KEY"
    )
