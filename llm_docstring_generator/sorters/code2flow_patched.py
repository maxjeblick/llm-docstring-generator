"""
Utility functions to customize code2flow library
"""
import logging
from contextlib import contextmanager
from unittest import mock

import code2flow
from code2flow import code2flow as code2flow_function
from code2flow.engine import make_file_group
from code2flow.model import LEAF_COLOR, NODE_COLOR, TRUNK_COLOR, Node


def code2flow_patched(raw_source_paths, output_file):
    """
    Patch code2flow library as follows:
    - make_file_group_patch: add original_filename to all nodes
    - to_dot_path: add original_filename to the node's attributes (these are now accessible due to the patch above)
    - fix the logging configuration format (code2flow changes it)
    - parse node names to their import name (we need the filenames for this, thus the steps above)
    """
    # Add file_group.original_filename = filename
    with mock.patch.object(code2flow.engine, "make_file_group", make_file_group_patch):
        # do not allow code2flow to overwrite the logging configuration
        with mock.patch.object(logging, "basicConfig", lambda *args, **kwargs: None):
            # parse filename from file_group.original_filename and add it to .dot attributes
            with patch_method(Node, "to_dot", to_dot_path):
                # too much noise otherwise
                with DisableLogger():
                    code2flow_function(
                        raw_source_paths=raw_source_paths,
                        output_file=output_file,
                        no_trimming=True,
                        language="py",
                        # skip_parse_errors for e.g.
                        # transformers/templates/adding_a_new_model/cookiecutter-template-{{cookiecutter.modelname}}/tokenization_{{cookiecutter.lowercase_modelname}}.py
                        skip_parse_errors=True,
                    )


class DisableLogger:
    def __enter__(self):
        logging.disable(logging.INFO)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


@contextmanager
def patch_method(cls, method_name, new_method):
    original_method = getattr(cls, method_name)
    setattr(cls, method_name, new_method)
    try:
        yield
    finally:
        setattr(cls, method_name, original_method)


def make_file_group_patch(tree, filename, extension):
    file_group = make_file_group(tree, filename, extension)
    # add original_filename to all nodes
    file_group.original_filename = filename
    for node in file_group.all_nodes():
        node.original_filename = filename
    return file_group


def to_dot_path(self):
    """
    Output for graphviz (.dot) files
    :rtype: str
    """

    attributes = {
        "label": self.label(),
        "name": self.name(),
        "shape": "rect",
        "style": "rounded,filled",
        "fillcolor": NODE_COLOR,
        # access original_filename set in make_file_group_patch
        "filename": self.original_filename,  # changed
    }
    if self.is_trunk:
        attributes["fillcolor"] = TRUNK_COLOR
    elif self.is_leaf:
        attributes["fillcolor"] = LEAF_COLOR

    ret = self.uid + " ["
    for k, v in attributes.items():
        ret += f'{k}="{v}" '
    ret += "]"
    return ret
