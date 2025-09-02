from dataclasses import dataclass

from sous.ingredient import Ingredient


@dataclass
class Prose:
    text: str
    ingredients: list[Ingredient]
