import click

from django_configuration_management.utils import load_env


@click.command()
@click.option("--environment", default="development", help="Your environment")
def main(environment):
    load_env(environment)
