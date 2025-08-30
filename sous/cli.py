import os
import pathlib
import time
from typing import Optional, cast

import click

from sous.downloader import Downloader
from sous.shopping_list import ShoppingList
from sous.todoist import Todoist
from sous.utils import Text


@click.group()
def cli() -> None:
    pass


@cli.command(name="import")
@click.argument("source")
@click.option("--json-file", help="Target for an intermediate recipe JSON file")
@click.option("--sous-file", help="Target for a .sous file")
def import_recipe(
    source: str, json_file: Optional[str] = None, sous_file: Optional[str] = None
) -> None:
    """Create a .sous file for the given recipe"""

    scraped_recipe = Downloader().download(source)

    if json_file:
        scraped_recipe.save(json_file)

    print(scraped_recipe.to_sous(sous_file))


@cli.command(name="dump")
@click.argument("url-file")
@click.argument("output-directory-path")
def dump_recipes(url_file: str, output_directory_path: str) -> None:
    """Dump JSON files for all the recipes in the given file of URLs"""

    downloader = Downloader()

    with open(url_file) as fh:
        for line in fh:
            url = line.strip()
            if not url:
                continue

            scraped_recipe = downloader.download(url)
            scraped_recipe.save(
                f"{output_directory_path}/{Text.kebab_case(scraped_recipe.title)}.json"
            )

            if downloader.delay:
                time.sleep(int(downloader.delay))


@cli.command()
@click.argument("dump_directory_path")
@click.argument("output_directory_path")
def archive(dump_directory_path: str, output_directory_path: str) -> None:
    """Convert recipe JSON files to .sous files in bulk"""

    downloader = Downloader()

    for dirpath, _, filenames in os.walk(dump_directory_path):
        for name in filenames:
            json_file_path = os.path.join("/", dirpath, name)
            sous_file_path = f"{output_directory_path}/{pathlib.Path(name).stem}.sous"

            scraped_recipe = downloader.download(json_file_path)
            scraped_recipe.to_sous(sous_file_path)


@cli.command()
@click.argument("recipes", nargs=-1)
@click.option(
    "--exclude",
    "-x",
    multiple=True,
    help="Exclude this ingredient from the shopping list",
)
@click.option(
    "--format",
    type=click.Choice(
        (ShoppingList.FORMAT_EXPANDED, ShoppingList.FORMAT_COMPACT),
        case_sensitive=False,
    ),
    default=ShoppingList.FORMAT_COMPACT,
    help="Format for items in the shopping list",
)
@click.option("--project-id", help="Identifier for a Todoist Project")
@click.option("--token-file", help="Path to a file containing a Todoist API token")
@click.option(
    "--export",
    is_flag=True,
    show_default=True,
    default=False,
    help="Export the shopping list to Todoist",
)
def shop(
    recipes: list[str],
    exclude: list[str],
    format: str,
    project_id: str,
    token_file: str,
    export: bool,
) -> None:
    """Build a shopping list for the given list of recipes"""

    if export and not project_id:
        project_id = click.prompt("Please enter a Todoist Project ID")

    token: Optional[str] = None

    if export and token_file:
        with open(token_file) as fh:
            token = fh.read().strip()

    if export and token is None:
        token = click.prompt("Please enter a Todoist API token", hide_input=True)

    if export and token is None:
        click.echo("You must provide a token for this operation")
        return

    click.echo(f"Building shopping list for {Text.pluralize('recipe', len(recipes))}")
    shopping_list = ShoppingList(recipes, exclude)

    if export:
        client = Todoist(cast(str, token))
        client.export(shopping_list, project_id, format)
    else:
        click.echo()
        for item in shopping_list.format(format):
            click.echo(item)
        click.echo()

    click.echo("Happy shopping! 🛍️")


if __name__ == "__main__":
    cli()
