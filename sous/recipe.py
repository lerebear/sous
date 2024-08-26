from functools import cached_property
from .document import Document
from .ingredient import Ingredient
from .prose import Prose


class Recipe:
    def __init__(self, filepath: str):
        self.document = Document(filepath)

    @cached_property
    def ingredients(self):
        ingredients: list[Ingredient] = []

        for paragraph in self.document.paragraphs:
            for line in paragraph:
                if isinstance(line, Ingredient):
                    ingredients.append(line)

                if isinstance(line, Prose):
                    ingredients.extend(line.ingredients)

        return ingredients
