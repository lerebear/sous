import re
from dataclasses import dataclass


@dataclass
class Comment:
    text: str

    RE = re.compile(r"^%\s+(?P<comment>.+)$")
