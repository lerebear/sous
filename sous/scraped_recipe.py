import json
from functools import cached_property
from typing import Any, Optional

from ingredient_parser import parse_ingredient

from sous.utils import Text

SOUS_FORMAT_VERSION = 1


class ScrapedRecipe:
    def __init__(self, recipe_json: dict[Any, Any]) -> None:
        self.recipe_json = recipe_json

    def save(self, output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.recipe_json, f, ensure_ascii=False, indent=2)

    def to_sous(self, output_file_path: Optional[str] = None) -> str:
        lines: list[str] = []
        lines.extend(self._title())
        lines.extend(self._frontmatter())
        lines.extend(self._intro())
        lines.extend(self._ingredients())
        lines.extend(self._steps())

        result = "\n".join(lines)

        if output_file_path:
            with open(output_file_path, "w") as fh:
                fh.write(result)

        return result

    def _frontmatter(self) -> list[str]:
        frontmatter = [
            f"@{attribute} {value}"
            for (attribute, value) in {
                "source": self.recipe_json.get("canonical_url", None),
                "author": self.recipe_json.get("author", None),
                "cook-time": self.recipe_json.get("cook_time", None),
                "prep-time": self.recipe_json.get("prep_time", None),
                "total-time": self.recipe_json.get("total_time", None),
                "yield": self.recipe_json.get("yields", None),
                "syntax": SOUS_FORMAT_VERSION,
            }.items()
            if value is not None
        ]

        result: list[str] = []
        if len(frontmatter):
            result.extend(frontmatter)
            result.append("")

        return result

    @cached_property
    def title(self) -> str:
        return self.recipe_json["title"]

    def _title(self) -> list[str]:
        return [f"# {self.title}", ""]

    def _intro(self) -> list[str]:
        if self.recipe_json["description"]:
            return [self.recipe_json["description"], ""]

        return []

    def _ingredients(self) -> list[str]:
        result: list[str] = []

        for index, raw_ingredient in enumerate(self.recipe_json["ingredients"]):
            parsed_ingredient = parse_ingredient(raw_ingredient)

            name = (
                parsed_ingredient.name[0].text
                if parsed_ingredient.name
                else f"{index + 1}"
            )
            prep = (
                f"{parsed_ingredient.preparation.text}"
                if parsed_ingredient.preparation
                else None
            )
            amount = (
                f"{{{parsed_ingredient.amount[0].text}}}"
                if parsed_ingredient.amount
                else "{}"
            )

            components = [
                f"{amount}[{name.lower()}]",
                prep,
            ]
            result.append(Text.join(" ", components))

        if len(result):
            result.append("")

        return result

    def _steps(self) -> list[str]:
        return [
            f"{instruction}\n" for instruction in self.recipe_json["instructions_list"]
        ]
