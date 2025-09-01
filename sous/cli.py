import os
import pathlib
import time
from typing import Optional

import click

from sous.cookbook import Cookbook
from sous.downloader import Downloader
from sous.shopping_list import ShoppingList
from sous.utils import Text

CONTEXT_SETTINGS: dict[str, list[str]] = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli() -> None:
    """a kitchen assistant"""
    pass


@cli.command(name="import", context_settings=CONTEXT_SETTINGS)
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


@cli.command(name="dump", context_settings=CONTEXT_SETTINGS)
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


@cli.command(context_settings=CONTEXT_SETTINGS)
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


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--cookbook",
    "-c",
    "cookbook_paths",
    default=[],
    multiple=True,
    help="Path to a directory containing .sous files",
)
@click.option(
    "--recipe",
    "-r",
    "recipe_paths",
    default=[],
    multiple=True,
    help="Path to a .sous file",
)
@click.option(
    "--format",
    type=click.Choice(
        (ShoppingList.FORMAT_EXPANDED, ShoppingList.FORMAT_COMPACT),
        case_sensitive=False,
    ),
    default=ShoppingList.FORMAT_EXPANDED,
    help="Format for items in the shopping list",
)
def shop(cookbook_paths: tuple[str], recipe_paths: tuple[str], format: str) -> None:
    """Build a shopping list from a collection of recipes"""
    cookbook = Cookbook(cookbook_paths, recipe_paths)
    shopping_list = ShoppingList.build(cookbook, format)

    if len(shopping_list.items):
        click.echo(f"\n{str(shopping_list)}\n")
        click.echo("Happy shopping! 🛍️")


if __name__ == "__main__":
    cli()
