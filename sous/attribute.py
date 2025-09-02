import re
from dataclasses import dataclass


@dataclass
class Attribute:
    name: str
    value: str

    RE = re.compile(r"^@(?P<name>[\w-]+)\s+(?P<value>.+)$")
