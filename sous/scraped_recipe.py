import json
import logging
from fractions import Fraction
from functools import cached_property
from typing import Any

from ingredient_parser import parse_ingredient
from ingredient_parser.dataclasses import IngredientAmount

from sous.utils import Text

SOUS_FORMAT_VERSION = 1
INGREDIENT_CONFIDENCE_THRESHOLD = 0.75

logger = logging.getLogger(__name__)


class ScrapedRecipe:
    def __init__(self, recipe_json: dict[Any, Any]) -> None:
        self.recipe_json = recipe_json

    def save(self, output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.recipe_json, f, ensure_ascii=False, indent=2)

    def to_sous(self, output_file_path: str | None = None) -> str:
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

        for sentence in self.recipe_json["ingredients"]:
            ingredient = parse_ingredient(sentence)
            logger.info(ingredient)

            if not ingredient.name:
                raise RuntimeError(
                    f"Failed to parse ingredient from sentence '{sentence}'"
                )

            for name in ingredient.name:
                if name.confidence < INGREDIENT_CONFIDENCE_THRESHOLD:
                    logger.warning(
                        f"Confidence for ingredient '{name.text}' is too low: "
                        f"{name.confidence} < {INGREDIENT_CONFIDENCE_THRESHOLD}"
                    )

            names = [name.text for name in ingredient.name]
            prep = f"{ingredient.preparation.text}" if ingredient.preparation else None
            amount = (
                f"{{{self._format_amount(ingredient.amount[0])}}}"
                if ingredient.amount
                else "{}"
            )

            components = [
                f"{amount}[{' | '.join([name.lower() for name in names])}]",
                prep,
            ]
            result.append(Text.join(" ", components))

        if len(result):
            result.append("")

        return result

    @staticmethod
    def _format_amount(amount: IngredientAmount) -> str:
        qty_str = ScrapedRecipe._format_fraction(amount.quantity)

        if amount.RANGE and amount.quantity != amount.quantity_max:
            max_str = ScrapedRecipe._format_fraction(amount.quantity_max)
            qty_str = f"{qty_str} - {max_str}"

        unit_str = str(amount.unit) if amount.unit else ""
        if unit_str:
            effective_qty = amount.quantity_max if amount.RANGE else amount.quantity
            if effective_qty > 1 and not unit_str.endswith("s"):
                unit_str += "s"
            qty_str = f"{qty_str} {unit_str}"

        return qty_str

    @staticmethod
    def _format_fraction(value: Fraction | str) -> str:
        if not isinstance(value, Fraction):
            return str(value)

        if value.denominator == 1:
            return str(value.numerator)

        whole = value.numerator // value.denominator
        remainder = value - whole
        if whole:
            return f"{whole} {remainder}"
        return str(value)

    def _steps(self) -> list[str]:
        return [
            f"{instruction}\n" for instruction in self.recipe_json["instructions_list"]
        ]
