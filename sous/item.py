from typing import Any


class Item:
    def __init__(self, name: str, quantities: list[str]) -> None:
        self.name = name
        self.quantities = quantities

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:  # noqa: ANN401
        return self.name == other.name

    def __ne__(self, other: Any) -> bool:  # noqa: ANN401
        return self.name != other.name

    def __str__(self) -> str:
        formatted_quantities = (
            f"({', '.join(self.quantities)})" if self.quantities else ""
        )
        return f"{self.name} {formatted_quantities}".strip()
