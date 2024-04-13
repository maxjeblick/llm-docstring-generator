from dataclasses import dataclass
from typing import Optional


@dataclass
class Import:
    import_name: str  # e.g. torch.nn
    class_or_function_name: Optional[str] = None  # e.g. Module
    method_name: Optional[str] = None  # e.g. forward

    def __post_init__(self):
        assert self.import_name, (
            f"import_name cannot be empty"
            f" {(self.import_name, self.class_or_function_name, self.method_name)}"
        )

    @property
    def complete_import_name(self) -> str:
        complete_import_name = self.import_name
        if self.class_or_function_name:
            complete_import_name += f".{self.class_or_function_name}"
        if self.method_name:
            complete_import_name += f".{self.method_name}"
        return complete_import_name

    def __hash__(self):
        # allows for == comparison
        return hash(self.complete_import_name)
