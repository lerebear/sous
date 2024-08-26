from collections import defaultdict

from .ingredient import Ingredient
from .item import Item
from .recipe import Recipe


class ShoppingList:
    FORMAT_COMPACT = "compact"
    FORMAT_EXPANDED = "expanded"

    def __init__(self, recipe_file_paths: list[str]):
        self.recipe_file_paths = recipe_file_paths
        self.items = self._build_items()

    def format(self, format: str = FORMAT_COMPACT) -> list[str]:
        result: list[str] = []

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

        quantities: dict[Ingredient, list[str]] = defaultdict(list)
        for ingredient in ingredients:
            if ingredient.quantity:
                quantities[ingredient].append(ingredient.quantity)

        return set(
            [Item(ingredient.id, quantities[ingredient]) for ingredient in ingredients]
        )
