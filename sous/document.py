import re

from .attribute import Attribute
from .comment import Comment
from .header import Header
from .ingredient import Ingredient
from .prose import Prose

type Node = Header | Attribute | Comment | Ingredient | Prose


class Document:
    HEADER_RE = re.compile(r"^(?P<level>#+)\s+(?P<name>.+)$")
    ATTRIBUTE_RE = re.compile(r"^@(?P<name>[\w-]+)\s+(?P<value>.+)$")
    COMMENT_RE = re.compile(r"^%\s+(?P<comment>.+)$")
    BLOCK_INGREDIENT_DEFINITION_RE = re.compile(
        r"^{(?P<quantity>[^}]*)}(?P<descriptors>[^[]*)\[(?P<id>[^,\]]+)\](?P<preparation>.*)$"
    )
    INLINE_INGREDIENT_DEFINITION_RE = re.compile(
        r"{(?P<quantity>[^}]*)}\[(?P<id>[^,\]]+)\]"
    )
    INGREDIENT_REFERENCE_RE = re.compile(r"\[(?P<ref>[^,\]]+)\](\((?P<id>[^)]+)\))?")

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
        header = self.HEADER_RE.match(line)
        if header:
            return Header(len(header.group("level")), header.group("name"))

        attribute = self.ATTRIBUTE_RE.match(line)
        if attribute:
            return Attribute(attribute.group("name"), attribute.group("value"))

        comment = self.COMMENT_RE.match(line)
        if comment:
            return Comment(comment.group("comment"))

        block_ingredient_def = self.BLOCK_INGREDIENT_DEFINITION_RE.match(line)
        if block_ingredient_def:
            return Ingredient(
                id=block_ingredient_def.group("id"),
                quantity=block_ingredient_def.group("quantity"),
                descriptors=block_ingredient_def.group("descriptors"),
                preparation=block_ingredient_def.group("preparation"),
            )

        inline_ingredients: list[Ingredient] = []
        for inline_ingredient_def in self.INLINE_INGREDIENT_DEFINITION_RE.finditer(
            line
        ):
            inline_ingredients.append(
                Ingredient(
                    id=inline_ingredient_def.group("id"),
                    quantity=inline_ingredient_def.group("quantity"),
                )
            )

        return Prose(line, inline_ingredients)
