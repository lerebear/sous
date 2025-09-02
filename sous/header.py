import re
from dataclasses import dataclass


@dataclass
class Header:
    level: int
    name: str

    RE = re.compile(r"^(?P<level>#+)\s+(?P<name>.+)$")
