from collections import defaultdict
from functools import cached_property
import re

import click

from todoist_api_python.api import TodoistAPI

HEADER_RE = re.compile("^(?P<level>#+)\s+(?P<name>.+)$")
ATTRIBUTE_RE = re.compile(r"^@(?P<name>[\w-]+)\s+(?P<value>.+)$")
COMMENT_RE = re.compile(r"^%\s+(?P<comment>.+)$")
BLOCK_INGREDIENT_DEFINITION_RE = re.compile(
    r"^{(?P<quantity>[^}]*)}(?P<descriptors>[^[]*)\[(?P<id>[^,\]]+)\](?P<preparation>.*)$"
)
INLINE_INGREDIENT_DEFINITION_RE = re.compile(
    r"{(?P<quantity>[^}]*)}\[(?P<id>[^,\]]+)\]"
)
INGREDIENT_REFERENCE_RE = re.compile(r"\[(?P<ref>[^,\]]+)\](\((?P<id>[^)]+)\))?")


def _join_available(separator, collection):
    return separator.join([e for e in collection if e])


class Ingredient:
    def __init__(
        self,
        id: str,
        quantity: str = None,
        descriptors: str = None,
        preparation: str = None,
    ):
        self.id = id
        self.quantity = quantity
        self.descriptors = descriptors
        self.preparation = preparation

    def __str__(self):
        return _join_available(
            " ",
            [
                self.quantity,
                self.descriptors,
                self.id,
                self.preparation,
            ],
        )

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id


class Header:
    def __init__(self, level: int, name: str):
        self.level = level
        self.name = name


class Attribute:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value


class Comment:
    def __init__(self, text: str):
        self.text = text


class Prose:
    def __init__(self, text: str, ingredients: list[Ingredient]):
        self.text = text
        self.ingredients = ingredients


class ShoppingList:
    FORMAT_COMPACT = "compact"
    FORMAT_EXPANDED = "expanded"

    def __init__(self, recipe_file_paths: list[str]):
        self.recipe_file_paths = recipe_file_paths
        self.items = self._build_items()

    def format(self, format: str = FORMAT_COMPACT):
        result = []

        if format == self.FORMAT_COMPACT:
            for item in self.items:
                uses = f"({len(item.quantities)})" if len(item.quantities) > 1 else ""
                result.append(f"{item.name} {uses}".strip())
        elif format == self.FORMAT_EXPANDED:
            for item in self.items:
                quantities = (
                    f"({', '.join(item.quantities)})" if item.quantities else ""
                )
                result.append(f"{item.name} {quantities}".strip())
        else:
            raise ValueError(f"Invalid shopping list format: '{format}'")

        return sorted(result)

    def _build_items(self):
        recipes = [Recipe(filepath) for filepath in self.recipe_file_paths]
        ingredients = [
            ingredient for recipe in recipes for ingredient in recipe.ingredients
        ]

        quantities = defaultdict(list)
        for ingredient in ingredients:
            if ingredient.quantity:
                quantities[ingredient].append(ingredient.quantity)

        return set(
            [Item(ingredient.id, quantities[ingredient]) for ingredient in ingredients]
        )


class Item:
    def __init__(self, name: str, quantities: list[str]):
        self.name = name
        self.quantities = quantities

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __str__(self):
        formatted_quantities = (
            f"({', '.join(self.quantities)})" if self.quantities else ""
        )
        return f"{self.name} {formatted_quantities}".strip()


class Document:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.paragraphs = []

        with open(filepath) as file:
            paragraph = []

            for line in file:
                contents = line.strip()

                if contents:
                    paragraph.append(self._parse_line(contents))
                elif len(paragraph):
                    self.paragraphs.append(paragraph)
                    paragraph = []

            if len(paragraph):
                self.paragraphs.append(paragraph)

    def summarize(self):
        result = []

        for paragraph in self.paragraphs:
            for line in paragraph:
                summary = type(line).__name__

                if summary == "Prose":
                    summary = f"{summary} ({len(line.ingredients)})"

                result.append(summary)

            result.append("")

        return "\n".join(result)

    def _parse_line(self, line):
        header = HEADER_RE.match(line)
        if header:
            return Header(len(header.group("level")), header.group("name"))

        attribute = ATTRIBUTE_RE.match(line)
        if attribute:
            return Attribute(attribute.group("name"), attribute.group("value"))

        comment = COMMENT_RE.match(line)
        if comment:
            return Comment(comment.group("comment"))

        block_ingredient_def = BLOCK_INGREDIENT_DEFINITION_RE.match(line)
        if block_ingredient_def:
            return Ingredient(
                id=block_ingredient_def.group("id"),
                quantity=block_ingredient_def.group("quantity"),
                descriptors=block_ingredient_def.group("descriptors"),
                preparation=block_ingredient_def.group("preparation"),
            )

        inline_ingredients = []
        for inline_ingredient_def in INLINE_INGREDIENT_DEFINITION_RE.finditer(line):
            inline_ingredients.append(
                Ingredient(
                    id=inline_ingredient_def.group("id"),
                    quantity=inline_ingredient_def.group("quantity"),
                )
            )

        return Prose(line, inline_ingredients)


class Recipe:
    def __init__(self, filepath: str):
        self.document = Document(filepath)

    @cached_property
    def ingredients(self):
        ingredients = []

        for paragraph in self.document.paragraphs:
            for line in paragraph:
                if isinstance(line, Ingredient):
                    ingredients.append(line)

                if isinstance(line, Prose):
                    ingredients.extend(line.ingredients)

        return ingredients


class Todoist:
    def __init__(self, token):
        self.token = token

    def export(
        self,
        shopping_list: ShoppingList,
        project_id: str,
        format: str = ShoppingList.FORMAT_COMPACT,
    ):
        client = TodoistAPI(self.token)
        items = shopping_list.format(format)

        with click.progressbar(
            items,
            label=f"Exporting {_pluralize('shopping list item', len(items))}",
        ) as progress_bar:
            for item in progress_bar:
                try:
                    client.add_task(content=item, project_id=project_id)
                except Exception as error:
                    click.echo(f"Error exporting item '{item}': {str(error)}", err=True)


@click.command()
@click.argument("recipes", nargs=-1)
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
def shop(recipes, format, project_id, token_file, export):
    """Build a shopping list for the given list of recipes"""

    if export and not project_id:
        project_id = click.prompt("Please enter a Todoist Project ID")

    token = None

    if export and token_file:
        with open(token_file) as fh:
            token = fh.read().strip()

    if export and token is None:
        token = click.prompt("Please enter a Todoist API token", hide_input=True)

    click.echo(f"Building shopping list for {_pluralize('recipe', len(recipes))}")
    shopping_list = ShoppingList(recipes)

    if export:
        client = Todoist(token)
        client.export(shopping_list, project_id, format)
    else:
        print()
        for item in shopping_list.format(format):
            print(item)
        print()

    click.echo("Happy shopping! 🛍️")


def _pluralize(singular_noun, count):
    pluralized = ""

    if count == 1:
        pluralized = singular_noun
    elif re.search("[sxz]$", singular_noun) or re.search(
        "[^aeioudgkprt]h$", singular_noun
    ):
        pluralized = re.sub("$", "es", singular_noun)
    elif re.search("[aeiou]y$", singular_noun):
        pluralized = re.sub("y$", "ies", singular_noun)
    else:
        pluralized = singular_noun + "s"

    return f"{count} {pluralized}"


if __name__ == "__main__":
    shop()
