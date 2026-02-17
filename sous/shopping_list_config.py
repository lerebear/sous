import tomllib
from collections import OrderedDict


class ShoppingListConfig:
    """
    Parses a TOML configuration file that defines how shopping list items
    should be grouped and ordered.

    Expected format:
        [dairy]
        items = ["milk", "butter", "eggs"]

        [produce]
        items = ["potatoes", "onions", "garlic"]
    """

    def __init__(self, path: str) -> None:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        self.categories: OrderedDict[str, list[str]] = OrderedDict()
        for category, value in data.items():
            if isinstance(value, dict) and "items" in value:
                self.categories[category] = [
                    item.lower() for item in value["items"]
                ]

    def category_for(self, item_name: str) -> str | None:
        """Return the category name for a given item, or None if uncategorized."""
        normalized = item_name.lower()
        for category, items in self.categories.items():
            if normalized in items:
                return category
        return None

    def sort_key(self, item_name: str) -> tuple[int, str]:
        """
        Return a sort key that orders items by:
        1. Category order (uncategorized items last)
        2. Alphabetical within each category
        """
        normalized = item_name.lower()
        for cat_index, (_, items) in enumerate(self.categories.items()):
            if normalized in items:
                return (cat_index, normalized)
        return (len(self.categories), normalized)
