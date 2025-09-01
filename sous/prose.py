from sous.ingredient import Ingredient


class Prose:
    def __init__(self, text: str, ingredients: list[Ingredient]) -> None:
        self.text = text
        self.ingredients = ingredients
