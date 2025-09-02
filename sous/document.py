from sous.attribute import Attribute
from sous.comment import Comment
from sous.header import Header
from sous.ingredient import Ingredient
from sous.prose import Prose

type Node = Header | Attribute | Comment | Ingredient | Prose


class Document:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.paragraphs: list[list[Node]] = []

        with open(filepath) as file:
            paragraph: list[Node] = []

            for line in file:
                contents = line.strip()

                if contents:
                    paragraph.append(self._parse_line(contents))
                elif len(paragraph):
                    self.paragraphs.append(paragraph)
                    paragraph = []

            if len(paragraph):
                self.paragraphs.append(paragraph)

    def summarize(self) -> str:
        result: list[str] = []

        for paragraph in self.paragraphs:
            for line in paragraph:
                summary = type(line).__name__

                if isinstance(line, Prose):
                    summary = f"{summary} ({len(line.ingredients)})"

                result.append(summary)

            result.append("")

        return "\n".join(result)

    def _parse_line(self, line: str) -> Node:
        header = Header.RE.match(line)
        if header:
            return Header(len(header.group("level")), header.group("name"))

        attribute = Attribute.RE.match(line)
        if attribute:
            return Attribute(attribute.group("name"), attribute.group("value"))

        comment = Comment.RE.match(line)
        if comment:
            return Comment(comment.group("comment"))

        block_ingredient_def = Ingredient.parse_block_definition(line)
        if block_ingredient_def:
            return block_ingredient_def

        return Prose(line, Ingredient.parse_inline_definitions(line))
