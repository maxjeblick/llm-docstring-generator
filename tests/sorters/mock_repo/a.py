# create 10 dummy functions
from dataclasses import dataclass
from typing import List


class DummyClass:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def __repr__(self):
        return f"DummyClass(prefix={self.prefix})"

    def __eq__(self, other):
        return self.prefix == other.prefix


def create_dummy_classes(prefix: str, n: int) -> List[DummyClass]:
    return [DummyClass(prefix) for _ in range(n)]


@dataclass
class DummyDataclass:
    prefix: str
    suffix: str

    def __repr__(self):
        return f"DummyDataclass(prefix={self.prefix}, suffix={self.suffix})"

    def __eq__(self, other):
        return self.prefix == other.prefix and self.suffix == other.suffix
