import click

from django_configuration_management.utils import (
    decrypt_value,
    dict_to_yml,
    gather_user_input,
    generate_fernet_key,
    load_env,
    yml_to_dict,
)


@click.group()
def manage():
    pass


@manage.command("upsert_secret")
@click.option("--environment", default="development", help="Your environment")
def upsert_secret(environment):
    load_env(environment)

    data = yml_to_dict(environment)
    key_name, key_value = gather_user_input()

    data[key_name] = {"value": key_value, "secret": True}

    dict_to_yml(data, environment)


@manage.command("reveal_secrets")
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


@manage.command("generate_key")
def generate_key():
    key = generate_fernet_key()

    print(f"Your key is: \n\n{key}\n")
    print(
        "Please store this in whichever .env-[environment] file you generated it for under the variable ENC_KEY"
    )


def main():
    manage()
