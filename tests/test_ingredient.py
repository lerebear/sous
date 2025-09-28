import unittest

from sous.ingredient import Ingredient

type IngredientArguments = tuple[str, str | None, str | None, str | None]


class TestIngredient(unittest.TestCase):
    def test_parse_block_definition(self) -> None:
        test_cases: list[tuple[str, IngredientArguments]] = [
            (
                "{3 cloves}[garlic], minced",
                (
                    "garlic",
                    "3 cloves",
                    None,
                    "minced",
                ),
            )
        ]

        for spec in test_cases:
            input_line, expected_ingredient_attributes = spec

            self.assertEqual(
                Ingredient(*expected_ingredient_attributes),
                Ingredient.parse_block_definition(input_line),
            )
