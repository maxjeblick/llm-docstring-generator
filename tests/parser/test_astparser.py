import ast
import textwrap

import astunparse
from llm_docstring_generator.parser.ast_parser import AstParser


def test_extract_function_nodes_empty():
    parser = AstParser("")
    assert parser.extract_function_nodes() == []


def test_extract_class_nodes_empty():
    parser = AstParser("")
    assert parser.extract_class_nodes() == []


def test_extract_method_nodes_from_class_node_empty():
    class_node = ast.parse("class Test: pass").body[0]
    parser = AstParser("")
    assert parser.extract_method_nodes_from_class_node(class_node) == []  # type: ignore


def test_get_docstring_line_no_docstring():
    function_node = ast.parse("def test(): pass").body[0]
    parser = AstParser("")
    assert parser.get_docstring_line(function_node) == 0  # type: ignore


def test_extract_function_nodes_non_empty():
    code = """
    def func1():
        pass
    def func2():
        pass
    """
    code = textwrap.dedent(code)
    parser = AstParser(code)
    assert len(parser.extract_function_nodes()) == 2


def test_extract_class_nodes_non_empty():
    code = """
    class Class1:
        pass
    class Class2:
        pass
    """
    code = textwrap.dedent(code)
    parser = AstParser(code)
    assert len(parser.extract_class_nodes()) == 2


def test_extract_method_nodes_from_class_node_non_empty():
    code = """
    class Test:
        def method1(self):
            pass
        def method2(self):
            pass
    """
    code = textwrap.dedent(code)
    class_node = ast.parse(code).body[0]
    parser = AstParser(code)
    assert len(parser.extract_method_nodes_from_class_node(class_node)) == 2  # type: ignore


def test_get_docstring_line_with_docstring():
    code = '''
    def test():
        """
        This is a docstring.
        """
        pass
    '''
    code = textwrap.dedent(code)
    function_node = ast.parse(code).body[0]
    parser = AstParser(code)
    assert parser.get_docstring_line(function_node) == 2  # type: ignore


def test_parse_class_node_with_nested_class():
    code = """
    class Outer:
        class Inner:
            pass
    """
    code = textwrap.dedent(code)
    parser = AstParser(code)
    class_node = parser.extract_class_nodes()[0]
    parsed_node = parser.parse_node(class_node)
    assert "class Inner" in parsed_node["codestring"]


def test_parse_class_node_with_method():
    code = """
    class Test:
        def method(self):
            pass
    """
    code = textwrap.dedent(code)
    parser = AstParser(code)
    class_node = parser.extract_class_nodes()[0]
    parsed_node = parser.parse_node(class_node)
    assert "def method(self)" in parsed_node["codestring"]


def test_parse_function_node_with_nested_function():
    code = """
    def outer():
        def inner():
            pass
    """
    code = textwrap.dedent(code)
    parser = AstParser(code)
    function_node = parser.extract_function_nodes()[0]
    parsed_node = parser.parse_node(function_node)
    assert "def inner()" in parsed_node["codestring"]


def test_parse_function_node_with_args():
    code = """
    def test(arg1: int, arg2: str):
        pass
    """
    code = textwrap.dedent(code)
    parser = AstParser(code)
    function_node = parser.extract_function_nodes()[0]
    parsed_node = parser.parse_node(function_node)
    assert "arg1: int" in parsed_node["codestring"]
    assert "arg2: str" in parsed_node["codestring"]
    assert parsed_node["codestring"] == code.strip("\n")


def test_parse_start_line():
    code = """
    def test(arg1: int, arg2: str):
        pass
    """
    code = textwrap.dedent(code).strip("\n")
    for i in range(20):
        parser = AstParser("\n" * i + code)
        function_node = parser.extract_function_nodes()[0]
        parsed_node = parser.parse_node(function_node)
        assert parsed_node["start_line"] == i
        assert parsed_node["codestring"] == code


def test_extract_function_nodes_does_not_include_classmethods():
    code = """
    class Test:
        def method(self):
            pass
        @classmethod
        def classmethod(cls):
            pass

    def foo():
        pass

    def bar():
        pass
    """
    code = textwrap.dedent(code)
    parser = AstParser(code)
    function_nodes = parser.extract_function_nodes()
    function_strings = [astunparse.unparse(node) for node in function_nodes]
    assert len(parser.extract_function_nodes()) == 2
    assert "method" not in function_strings[0]
    assert "method" not in function_strings[1]

    assert "foo" in function_strings[0]
    assert "bar" in function_strings[1]


def test_extract_method_extracts_methods():
    code = """
    class Test:
        def method(self):
            pass
        @classmethod
        def classmethod(cls):
            pass

    def foo():
        pass

    def bar():
        pass
    """
    code = textwrap.dedent(code)
    parser = AstParser(code)
    class_node = parser.extract_class_nodes()[0]
    method_nodes = parser.extract_method_nodes_from_class_node(class_node)
    method_strings = [astunparse.unparse(node) for node in method_nodes]

    assert len(method_nodes) == 2
    assert "def method(self)" in method_strings[0]
    assert "def classmethod(cls)" in method_strings[1]
