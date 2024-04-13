from dataclasses import dataclass, field
from typing import List, Optional

from llm_docstring_generator.python_files.imports import Import


@dataclass
class CodeObject:
    import_: Import  # how you would import the function, e.g. Import('os', 'path', 'join') for os.path.join
    # other functions/classes/methods this function calls.
    import_dependencies: List[Import]
    codestring: str  # contains complete function code, minus decorators
    docstring: Optional[str]  # the docstring of the function, if it exists
    docstring_line: Optional[int]  # start line of the docstring
    start_line: int  # start line of the function in the file
    end_line: int  # end line of the function in the file

    llm_response: str = ""

    @property
    def complete_import_name(self) -> str:
        return self.import_.complete_import_name

    def __str__(self):
        return self.codestring

    def __eq__(self, other):
        return (
            self.codestring == other.codestring
            and self.start_line == other.start_line
            and self.end_line == other.end_line
            and self.import_.import_name == other.import_.import_name
        )


@dataclass
class Function(CodeObject):
    pass


@dataclass
class Class(CodeObject):
    methods: List[Function] = field(default_factory=list)
