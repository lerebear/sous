from collections import defaultdict
import re

import click

from todoist_api_python.api import TodoistAPI

EXPRESSIONS = {
    "id": r"\[(?P<id>[^]]+)\]",  # This is synonymous with link
    "link": r"\[(?P<link>[^]]+)\]",  # This is synonymous with id
    "ref": r"\[(?P<ref>[^]]+)\]",
    "description": r"(?P<description>[^{]*)",
    "optional": r"(?P<optional>\?)?",
    "quantity": r"\{(?P<quantity>[^}]*)\}",
}

CANONICAL_INGREDIENT_RE = re.compile(
    r"^{id}(:(\s+{description})?(\s+{quantity}{optional})?)?$".format(**EXPRESSIONS)
)
INLINE_INGREDIENT_RE = re.compile(r"{link}{quantity}{optional}".format(**EXPRESSIONS))
INGREDIENT_REFERENCE_RE = re.compile(r"^{link}{ref}{quantity}?$".format(**EXPRESSIONS))


class Ingredient:
    def __init__(
        self,
        id: str,
        description: str = None,
        quantity: str = None,
        optional: bool = False,
    ):
        self.id = id
        self.description = description
        self.quantity = quantity
        self.optional = optional

    def __str__(self):
        components = [
            self.quantity,
            self.description or self.id,
            "(optional)" if self.optional else None,
        ]
        return " ".join([s for s in components if s])

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id


class ShoppingList:
    FORMAT_DEFAULT = "default"
    FORMAT_COMPACT = "compact"

    def __init__(self, recipe_file_paths: list[str]):
        self.recipe_file_paths = recipe_file_paths
        self.items = self._build_items()

    def format(self, format: str = FORMAT_DEFAULT):
        result = []

        if format == self.FORMAT_COMPACT:
            for item in self.items:
                uses = f"({len(item.quantities)})" if len(item.quantities) > 1 else ""
                result.append(f"{item.name} {uses}".strip())
        elif format == self.DEFAULT:
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
                    paragraph.append(contents)
                elif len(paragraph):
                    self.paragraphs.append(paragraph)
                    paragraph = []

            if len(paragraph):
                self.paragraphs.append(paragraph)


class Recipe:
    def __init__(self, filepath: str):
        self.document = Document(filepath)
        self.ingredients = []

        for paragraph in Document(filepath).paragraphs:
            for line in paragraph:
                canonical = CANONICAL_INGREDIENT_RE.match(line)

                if canonical:
                    self.ingredients.append(
                        Ingredient(
                            id=canonical.group("id"),
                            description=canonical.group("description"),
                            quantity=canonical.group("quantity"),
                            optional=(canonical.group("optional") is not None),
                        )
                    )
                    continue

                for inline in INLINE_INGREDIENT_RE.finditer(line):
                    self.ingredients.append(
                        Ingredient(
                            id=inline.group("link"),
                            quantity=inline.group("quantity"),
                            optional=(inline.group("optional") is not None),
                        )
                    )
                    continue

    def ingredients(self):
        pass


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
@click.argument("project-id")
@click.argument("recipes", nargs=-1)
@click.option("--token-file", help="Path to a file containing a Todoist API token")
def shop(project_id, recipes, token_file):
    """Export a shopping list for the given list of recipes to Todoist"""
    token = None

    if token_file:
        with open(token_file) as fh:
            token = fh.read().strip()

    if token is None:
        token = click.prompt("Please enter a Todoist API token", hide_input=True)

    click.echo(f"Building shopping list for {_pluralize('recipe', len(recipes))}")
    shopping_list = ShoppingList(recipes)

    client = Todoist(token)
    client.export(shopping_list, project_id)

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
