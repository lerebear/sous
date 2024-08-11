import os
from pathlib import Path
import sys
from ingredient_parser import parse_ingredient
from recipe_scrapers import scrape_html
import requests
import urllib.robotparser
import json
import time
import re

import click
import yaml

SOUS_FORMAT_VERSION = 0
NYT_COOKING_BASE_URL = "https://cooking.nytimes.com"
NYT_COOKING_ROBOTS_URL = f"{NYT_COOKING_BASE_URL}/robots.txt"


def _kebab_case(sentence):
    sentence = sentence.lower()
    sentence = re.sub(r"[^\w\s]", "", sentence)  # Remove punctuation
    sentence = re.sub(r"\s+", "-", sentence)  # Replace spaces with underscores
    return sentence


def download_several_nyt_recipes(recipe_urls, target_directory):
    robots_parser = _robots_file_parser(NYT_COOKING_ROBOTS_URL)

    for url in recipe_urls:
        recipe = _download_nyt_recipe(url, robots_parser)
        _save_recipe_json(recipe, _recipe_path(recipe, target_directory))

        delay = robots_parser.crawl_delay("*")
        if delay:
            print(f"Sleeping {delay} seconds as per requested crawl delay")
            time.sleep(int(delay))


def _robots_file_parser(root_url):
    robots = urllib.robotparser.RobotFileParser(root_url)
    robots.read()
    return robots


def _download_nyt_recipe(url, robots_parser=None):
    recipe = None

    if robots_parser is None:
        robots_parser = _robots_file_parser(NYT_COOKING_ROBOTS_URL)

    if robots_parser.can_fetch("*", url):
        print(f"Downloading {url}")
        recipe = scrape_html(requests.get(url).content, org_url=url)

    return recipe


def _download_arbitrary_recipe(url, robots_parser=None):
    print(f"Downloading {url}")
    return scrape_html(requests.get(url).content, org_url=url, wild_mode=True)


def _recipe_path(recipe, target_directory):
    return (f"{target_directory}/{_kebab_case(recipe.title())}.json",)


def _save_recipe_json(recipe, output_path=None):
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(recipe.to_json(), f, ensure_ascii=False, indent=2)


def _json_to_sous(recipe, sous_file_path=None):
    lines = []
    lines.extend(_frontmatter(recipe))
    lines.extend(_title(recipe))
    lines.extend(_intro(recipe))
    lines.extend(_ingredients(recipe))
    lines.extend(_steps(recipe))

    result = "\n".join(lines)

    if sous_file_path:
        with open(sous_file_path, "w") as fh:
            fh.write(result)

    return result


def _frontmatter(recipe):
    frontmatter = {
        attribute: value
        for (attribute, value) in {
            "source": recipe.get("canonical_url", None),
            "author": recipe.get("author", None),
            "cook-time": recipe.get("cook_time", None),
            "prep-time": recipe.get("prep_time", None),
            "total-time": recipe.get("total_time", None),
            "yield": recipe.get("yields", None),
            "sous-version": SOUS_FORMAT_VERSION,
        }.items()
        if value is not None
    }

    result = []
    if len(frontmatter):
        result.append("---")
        result.extend(
            yaml.dump(frontmatter, default_flow_style=False).strip().split("\n")
        )
        result.append("---")
        result.append("")

    return result


def _title(recipe):
    return [recipe["title"], ""]


def _intro(recipe):
    if recipe["description"]:
        return [recipe["description"], ""]

    return []


def _ingredients(recipe):
    result = []

    for index, raw_ingredient in enumerate(recipe["ingredients"]):
        parsed_ingredient = parse_ingredient(raw_ingredient)

        name = parsed_ingredient.name.text if parsed_ingredient.name else f"{index + 1}"
        prep = (
            f"{parsed_ingredient.preparation.text}"
            if parsed_ingredient.preparation
            else None
        )
        amount = (
            f"{{{parsed_ingredient.amount[0].text}}}"
            if parsed_ingredient.amount
            else None
        )

        description = ", ".join([c for c in [name, prep] if c])

        components = [
            f"[{name.lower()}]:",
            description,
            amount,
        ]
        result.append(" ".join([c for c in components if c is not None]).strip(","))

    if len(result):
        result.append("")

    return result


def _steps(recipe):
    return [f"{instruction}\n" for instruction in recipe["instructions_list"]]


def _convert_recipes():
    for dirpath, dirnames, filenames in os.walk(
        "/Users/lerebear/lerebear/sous/recipes"
    ):
        for name in filenames:
            json_file_path = os.path.join("/", dirpath, name)
            sous_file_path = f"/Users/lerebear/Dropbox/cookbook/{Path(name).stem}.sous"

            recipe_json = None
            with open(json_file_path) as fh:
                recipe_json = json.load(fh)

            _json_to_sous(recipe_json, sous_file_path)


def _nyt_recipe_to_sous(url, output_json_file, output_sous_file):
    return _recipe_to_sous(_download_nyt_recipe(url), output_json_file, output_sous_file)


def _arbitrary_recipe_to_sous(url, output_json_file, output_sous_file):
    return _recipe_to_sous(_download_arbitrary_recipe(url), output_json_file, output_sous_file)


def _recipe_to_sous(recipe, output_json_file, output_sous_file):
    _save_recipe_json(recipe, output_json_file)
    return _json_to_sous(recipe.to_json(), output_sous_file)


def recipe_json_to_sous(recipe_json_file, output_sous_file):
    with open(recipe_json_file) as fh:
        return _json_to_sous(json.load(fh), output_sous_file)


@click.command(name="import")
@click.argument("source")
@click.option("--json-file", help="Target for an intermediate recipe JSON file")
@click.option("--sous-file", help="Target for a .sous file")
def import_recipe(source, json_file=None, sous_file=None):
    """Create a .sous file for the given recipe"""

    sous = None

    if source.startswith("http") and source.startswith(NYT_COOKING_ROBOTS_URL):
        sous = _nyt_recipe_to_sous(source, json_file, sous_file)
    elif source.startswith("http"):
        sous = _arbitrary_recipe_to_sous(source, json_file, sous_file)
    else:
        sous = recipe_json_to_sous(source, sous_file)

    print(sous)


if __name__ == "__main__":
    import_recipe()
