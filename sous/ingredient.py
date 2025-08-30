from typing import Any

from .utils import Text


class Ingredient:
    def __init__(
        self,
        id: str,
        quantity: str | None = None,
        descriptors: str | None = None,
        preparation: str | None = None,
    ) -> None:
        self.id = id
        self.quantity = quantity
        self.descriptors = descriptors
        self.preparation = preparation

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

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:  # noqa: ANN401
        return self.id == other.id

    def __ne__(self, other: Any) -> bool:  # noqa: ANN401
        return self.id != other.id
