import os
import tempfile
import unittest

from sous.ingredient import Ingredient
from sous.shopping_list import ShoppingList
from sous.shopping_list_config import ShoppingListConfig


class TestShoppingListConfig(unittest.TestCase):
    def test_parses_categories_from_toml(self) -> None:
        toml_content = b"""
[dairy]
items = ["milk", "butter"]

[produce]
items = ["potatoes", "onions"]
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()

            config = ShoppingListConfig(f.name)

        os.unlink(f.name)

        self.assertEqual(list(config.categories.keys()), ["dairy", "produce"])
        self.assertEqual(config.categories["dairy"], ["milk", "butter"])
        self.assertEqual(config.categories["produce"], ["potatoes", "onions"])

    def test_category_for_returns_matching_category(self) -> None:
        toml_content = b"""
[dairy]
items = ["milk", "butter"]

[produce]
items = ["potatoes"]
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()

            config = ShoppingListConfig(f.name)

        os.unlink(f.name)

        self.assertEqual(config.category_for("milk"), "dairy")
        self.assertEqual(config.category_for("potatoes"), "produce")

    def test_category_for_is_case_insensitive(self) -> None:
        toml_content = b"""
[dairy]
items = ["Milk"]
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()

            config = ShoppingListConfig(f.name)

        os.unlink(f.name)

        self.assertEqual(config.category_for("milk"), "dairy")
        self.assertEqual(config.category_for("MILK"), "dairy")

    def test_category_for_returns_none_for_unknown_items(self) -> None:
        toml_content = b"""
[dairy]
items = ["milk"]
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()

            config = ShoppingListConfig(f.name)

        os.unlink(f.name)

        self.assertIsNone(config.category_for("garlic"))

    def test_sort_key_orders_by_category_then_alphabetically(self) -> None:
        toml_content = b"""
[dairy]
items = ["milk", "butter"]

[produce]
items = ["potatoes", "onions"]
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()

            config = ShoppingListConfig(f.name)

        os.unlink(f.name)

        # dairy items come before produce items
        self.assertLess(config.sort_key("butter"), config.sort_key("onions"))
        # within dairy, butter comes before milk (alphabetically)
        self.assertLess(config.sort_key("butter"), config.sort_key("milk"))
        # within produce, onions comes before potatoes (alphabetically)
        self.assertLess(config.sort_key("onions"), config.sort_key("potatoes"))
        # uncategorized items come last
        self.assertLess(config.sort_key("milk"), config.sort_key("garlic"))


class TestShoppingListGroupedFormat(unittest.TestCase):
    def _make_config(self, toml_content: bytes) -> ShoppingListConfig:
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            config = ShoppingListConfig(f.name)
        os.unlink(f.name)
        return config

    def test_grouped_format_orders_by_config(self) -> None:
        config = self._make_config(b"""
[produce]
items = ["garlic", "broccoli"]

[spices]
items = ["red pepper flakes", "kosher salt"]
""")
        ingredients = [
            Ingredient(id="kosher salt"),
            Ingredient(id="broccoli", quantity="2"),
            Ingredient(id="garlic", quantity="3 cloves"),
            Ingredient(id="red pepper flakes"),
        ]

        shopping_list = ShoppingList(ingredients, ShoppingList.FORMAT_EXPANDED, config)
        formatted = shopping_list._format()

        self.assertEqual(formatted, [
            "[produce]",
            "broccoli (2)",
            "garlic (3 cloves)",
            "",
            "[spices]",
            "kosher salt",
            "red pepper flakes",
        ])

    def test_grouped_format_puts_uncategorized_items_last(self) -> None:
        config = self._make_config(b"""
[produce]
items = ["garlic"]
""")
        ingredients = [
            Ingredient(id="garlic", quantity="3 cloves"),
            Ingredient(id="olive oil"),
            Ingredient(id="butter"),
        ]

        shopping_list = ShoppingList(ingredients, ShoppingList.FORMAT_EXPANDED, config)
        formatted = shopping_list._format()

        self.assertEqual(formatted, [
            "[produce]",
            "garlic (3 cloves)",
            "",
            "[other]",
            "butter",
            "olive oil",
        ])

    def test_grouped_format_compact(self) -> None:
        config = self._make_config(b"""
[dairy]
items = ["milk"]
""")
        milk = Ingredient(id="milk", quantity="1 cup")
        ingredients = [milk, milk, Ingredient(id="garlic")]

        shopping_list = ShoppingList(ingredients, ShoppingList.FORMAT_COMPACT, config)
        formatted = shopping_list._format()

        self.assertEqual(formatted, [
            "[dairy]",
            "milk (2)",
            "",
            "[other]",
            "garlic",
        ])

    def test_without_config_sorts_alphabetically(self) -> None:
        ingredients = [
            Ingredient(id="garlic", quantity="3 cloves"),
            Ingredient(id="broccoli", quantity="2"),
            Ingredient(id="olive oil"),
        ]

        shopping_list = ShoppingList(ingredients, ShoppingList.FORMAT_EXPANDED)
        formatted = shopping_list._format()

        self.assertEqual(formatted, [
            "broccoli (2)",
            "garlic (3 cloves)",
            "olive oil",
        ])
