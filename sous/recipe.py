from functools import cached_property

from sous.document import Document, Header
from sous.ingredient import Ingredient
from sous.prose import Prose


class Recipe:
    def __init__(self, filepath: str) -> None:
        self.document = Document(filepath)

    @property
    def name(self) -> str | None:
        for paragraph in self.document.paragraphs:
            for line in paragraph:
                if isinstance(line, Header):
                    return line.name

    @cached_property
    def ingredients(self) -> list[Ingredient]:
        ingredients: list[Ingredient] = []

        for paragraph in self.document.paragraphs:
            for line in paragraph:
                if isinstance(line, Ingredient):
                    ingredients.append(line)

                if isinstance(line, Prose):
                    ingredients.extend(line.ingredients)

        return ingredients
