from typing import Any


class Item:
    def __init__(self, name: str, quantities: list[str]):
        self.name = name
        self.quantities = quantities

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: Any):
        return self.name == other.name

    def __ne__(self, other: Any):
        return self.name != other.name

    def __str__(self):
        formatted_quantities = (
            f"({', '.join(self.quantities)})" if self.quantities else ""
        )
        return f"{self.name} {formatted_quantities}".strip()
