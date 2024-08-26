from typing import Any
from .utils import Text


class Ingredient:
    def __init__(
        self,
        id: str,
        quantity: str | None = None,
        descriptors: str | None = None,
        preparation: str | None = None,
    ):
        self.id = id
        self.quantity = quantity
        self.descriptors = descriptors
        self.preparation = preparation

    def __str__(self):
        return Text.join(
            " ",
            [
                self.quantity,
                self.descriptors,
                self.id,
                self.preparation,
            ],
        )

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other: Any):
        return self.id == other.id

    def __ne__(self, other: Any):
        return self.id != other.id
