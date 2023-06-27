"""This module is the entry point for the application."""
from io import StringIO
import os

import click
import openai

from .generator import Generator


@click.command()
@click.argument("project_name")
@click.option(
    "--api-key",
    "-k",
    envvar="OPENAI_API_KEY",
    help="Your OpenAI API key.",
)
@click.option(
    "--file",
    "-f",
    type=click.File("w"),
    help="The path to the file to write the README to.",
    default="README.md",
)
def run(project_name: str, api_key: str, file: StringIO):
    """Generate a README for a project.

    Args:
        project_name: The name of the project.
        api_key: Your OpenAI API key.
    """
    if api_key is None:
        try:
            with open(
                click.get_app_dir("readme-creator") + "/api_key", "r", encoding="utf-8"
            ) as config_file:
                api_key = config_file.read()
        except FileNotFoundError:
            api_key = click.prompt(
                "OpenAI API key",
                type=str,
                hide_input=True,
            )
            os.makedirs(click.get_app_dir("readme-creator"), exist_ok=True)
            with open(
                click.get_app_dir("readme-creator") + "/api_key", "w", encoding="utf-8"
            ) as config_file:
                config_file.write(api_key)
    openai.api_key = api_key
    os.makedirs(click.get_app_dir("readme-creator") + "/generated", exist_ok=True)
    generator = Generator(
        project_name, click.get_app_dir("readme-creator") + "/generated"
    )
    readme = generator.run()
    file.write(readme)
