import re
from typing import Any


class Text:
    @staticmethod
    def pluralize(singular_noun: str, count: int) -> str:
        pluralized = ""

        if count == 1:
            pluralized = singular_noun
        elif re.search("[sxz]$", singular_noun) or re.search(
            "[^aeioudgkprt]h$", singular_noun
        ):
            pluralized = re.sub("$", "es", singular_noun)
        elif re.search("[aeiou]y$", singular_noun):
            pluralized = re.sub("y$", "ies", singular_noun)
        else:
            pluralized = singular_noun + "s"

        return f"{count} {pluralized}"

    @staticmethod
    def join(separator: str, collection: list[Any]) -> str:
        return separator.join([e for e in collection if e])

    @staticmethod
    def kebab_case(sentence: str) -> str:
        sentence = sentence.lower()
        sentence = re.sub(r"[^\w\s-]", "", sentence)  # Remove punctuation
        sentence = re.sub(r"\s+", "-", sentence)  # Replace spaces with underscores
        return sentence
