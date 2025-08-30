import click
from todoist_api_python.api import TodoistAPI

from .shopping_list import ShoppingList
from .utils import Text


class Todoist:
    def __init__(self, token: str) -> None:
        self.token = token

    def export(
        self,
        shopping_list: ShoppingList,
        project_id: str,
        format: str = ShoppingList.FORMAT_COMPACT,
    ) -> None:
        client = TodoistAPI(self.token)
        items = shopping_list.format(format)

        with click.progressbar(
            items,
            label=f"Exporting {Text.pluralize('shopping list item', len(items))}",
        ) as progress_bar:
            for item in progress_bar:
                try:
                    client.add_task(content=item, project_id=project_id)  # type: ignore
                except Exception as error:
                    click.echo(f"Error exporting item '{item}': {str(error)}", err=True)
