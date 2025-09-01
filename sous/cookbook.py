import os
import sys

from sous.recipe import Recipe

SOUS_FILE_EXTENSION = ".sous"


class Cookbook:
    def __init__(self, cookbook_paths: tuple[str], recipe_paths: tuple[str]) -> None:
        collated_recipe_paths: list[str] = [p for p in recipe_paths]

        for cookbook_path in cookbook_paths:
            for root, _, files in os.walk(cookbook_path):
                for file in files:
                    _, extension = os.path.splitext(file)
                    if extension == SOUS_FILE_EXTENSION:
                        collated_recipe_paths.append(os.path.join(root, file))

        self.recipes = []
        for filepath in collated_recipe_paths:
            recipe = Recipe(filepath)
            if recipe.name:
                self.recipes.append(recipe)
            else:
                sys.stderr.write(f"Ignoring recipe with no name at {filepath}\n")
