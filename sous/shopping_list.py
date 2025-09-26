from collections import defaultdict
from typing import cast

from simple_term_menu import TerminalMenu

from sous.cookbook import Cookbook
from sous.ingredient import Ingredient
from sous.item import Item
from sous.recipe import Recipe


class ShoppingList:
    FORMAT_COMPACT = "compact"
    FORMAT_EXPANDED = "expanded"
    FORMATS = [FORMAT_COMPACT, FORMAT_EXPANDED]

    @classmethod
    def build(cls, cookbook: Cookbook, format: str) -> "ShoppingList":
        selected_ingredients: list[Ingredient] = []

        while True:
            recipe = cls.__select_recipe(cookbook)
            if recipe is None:
                break
            selected_ingredients.extend(cls.__select_ingredients(recipe))

        return cls(selected_ingredients, format)

    def __init__(self, ingredients: list[Ingredient], format: str) -> None:
        if format not in self.FORMATS:
            raise ValueError(f"Invalid shopping list format: '{self.format}'")

        quantities: dict[Ingredient, list[str]] = defaultdict(list)
        for ingredient in ingredients:
            if ingredient.quantity:
                quantities[ingredient].append(ingredient.quantity)

        self.items = set(
            [Item(ingredient.id, quantities[ingredient]) for ingredient in ingredients]
        )
        self.format = format

    def __str__(self) -> str:
        return "\n".join(self._format())

    def _format(self) -> list[str]:
        result: list[str] = []

        if self.format == self.FORMAT_COMPACT:
            for item in self.items:
                uses = f"({len(item.quantities)})" if len(item.quantities) > 1 else ""
                result.append(f"{item.name} {uses}".strip())
        elif self.format == self.FORMAT_EXPANDED:
            for item in self.items:
                quantities = (
                    f"({', '.join(item.quantities)})" if item.quantities else ""
                )
                result.append(f"{item.name} {quantities}".strip())

        return sorted(result)

    @classmethod
    def __select_recipe(cls, cookbook: Cookbook) -> Recipe | None:
        recipes_by_name: dict[str, Recipe] = {r.name: r for r in cookbook.recipes}
        recipe_names: list[str] = list(recipes_by_name.keys())
        recipe_selection_menu = TerminalMenu(
            recipe_names, title="Please select a recipe:\n", show_search_hint=True
        )
        index: int | None = cast(int | None, recipe_selection_menu.show())
        return recipes_by_name[recipe_names[index]] if index is not None else None

    @classmethod
    def __select_ingredients(cls, recipe: Recipe) -> list[Ingredient]:
        ingredients_by_id: dict[str, Ingredient] = {
            ingredient.id: ingredient for ingredient in recipe.ingredients
        }
        ingredient_ids: list[str] = list(ingredients_by_id.keys())
        ingredient_selection_menu = TerminalMenu(
            ingredient_ids,
            title="Please select ingredients:\n",
            multi_select=True,
            multi_select_empty_ok=True,
            multi_select_keys=" x",
            show_multi_select_hint=True,
            preselected_entries=list(range(len(ingredient_ids))),
        )
        ingredient_id_indices = ingredient_selection_menu.show()

        if ingredient_id_indices is None:
            return []

        return [
            ingredients_by_id[ingredient_ids[index]] for index in cast(tuple[int], ingredient_id_indices)
        ]
