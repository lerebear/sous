from .ingredient import Ingredient


class Prose:
    def __init__(self, text: str, ingredients: list[Ingredient]):
        self.text = text
        self.ingredients = ingredients
