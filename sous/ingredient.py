import re
import string
from dataclasses import dataclass
from typing import Optional

from sous.utils import Text


@dataclass
class Ingredient:
    id: str
    quantity: str | None = None
    descriptors: str | None = None
    preparation: str | None = None

    BLOCK_DEFINITION_RE = re.compile(
        r"^{(?P<quantity>[^}]*)}(?P<descriptors>[^[]*)\[(?P<id>[^,\]]+)\](?P<preparation>.*)$"
    )

    INLINE_DEFINITION_RE = re.compile(r"{(?P<quantity>[^}]*)}\[(?P<id>[^,\]]+)\]")

    REFERENCE_RE = re.compile(r"\[(?P<ref>[^,\]]+)\](\((?P<id>[^)]+)\))?")

    @classmethod
    def parse_block_definition(cls, line: str) -> Optional["Ingredient"]:
        block_ingredient_def = cls.BLOCK_DEFINITION_RE.match(line)
        if not block_ingredient_def:
            return None

        return Ingredient(
            id=block_ingredient_def.group("id"),
            quantity=block_ingredient_def.group("quantity"),
            descriptors=(
                block_ingredient_def.group("descriptors")
                .strip(string.punctuation)
                .strip()
                or None
            ),
            preparation=(
                block_ingredient_def.group("preparation")
                .strip(string.punctuation)
                .strip()
                or None
            ),
        )

    @classmethod
    def parse_inline_definitions(cls, line: str) -> list["Ingredient"]:
        inline_ingredients: list[Ingredient] = []

        for inline_ingredient_def in Ingredient.INLINE_DEFINITION_RE.finditer(line):
            inline_ingredients.append(
                Ingredient(
                    id=inline_ingredient_def.group("id"),
                    quantity=inline_ingredient_def.group("quantity"),
                )
            )

        return inline_ingredients

    def __str__(self) -> str:
        return Text.join(
            " ",
            [
                self.quantity,
                self.descriptors,
                self.id,
                self.preparation,
            ],
        )
