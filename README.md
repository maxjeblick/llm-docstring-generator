# LLM Docstring Generator

## Automatically Generate Code Docstrings Using LLMs

<p align="left">
    <img src="/static/image.jpg" width="50%" />
</p>

The `llm-docstring-generator` provides:

1. A pipeline that **automatically creates docstrings** using Large Language Models (LLMs).
2. Utilization of a **hierarchical code dependency structure** to enrich the LLM model's context, enhancing the quality of annotations.
3. A **flexible** and **customizable** design, allowing adjustments to specific needs.

## Table of Contents

- [Getting Started](#getting-started)
- [Why This Repository?](#why-this-repository)
- [Workflow](#workflow)
- [Command-Line Interface](#command-line-interface)
- [Possible Additional Use-Cases](#possible-additional-use-cases)
- [Limitations](#limitations)
- [FAQ/Troubleshooting](#faqtroubleshooting)
- [Installation](#installation)
- [Similar Projects](#similar-projects)
- [Disclaimer](#disclaimer)

## Getting Started

To begin annotating your code, install the package using:

```bash
pip install llm-docstring-generator
```

You might need to install some system dependencies first (replace `python3.10-dev` with your python version):

```bash
sudo apt-get update && sudo apt-get install -y python3.10-dev graphviz libgraphviz-dev pkg-config
```

Next, run the following Python script to annotate a repository located at `my_repo_path` and save the annotated version to `my_repo_annotated`:

```python
from llm_docstring_generator import run_code_annotation_pipeline
import os

os.environ["OPENAI_API_KEY"] = "your_api_key"

run_code_annotation_pipeline(
    repository_name="my_repo",
    repository_path="my_repo_path",
    new_repository_path="my_repo_annotated",
    model="gpt-4-turbo",  # use "debug" for testing
    max_prompt_token_length=2048,
)
```

For a more detailed example on customization, please refer to the example folder.

## Why This Repository?

While several tools can autogenerate code annotations, this repository uniquely utilizes the **hierachical structure of code imports** to generate more contextual and accurate docstrings.

As, an example, the `.fit_transform` method of [Bertopic](https://github.com/MaartenGr/BERTopic/tree/master) looks like:
```python
...
    def fit_transform(self, ...):
        ...
        # Extract embeddings
        if embeddings is None:
            logger.info("Embedding - Transforming documents to embeddings.")
            self.embedding_model = select_backend(self.embedding_model,
                                                  language=self.language)
            embeddings = self._extract_embeddings(documents.Document.values.tolist(),
                                                  images=images,
                                                  method="document",
                                                  verbose=self.verbose)
...
```
For an LLM to be able to create a comprehensive docstring for `fit_transform`, it is useful to
- First annotate `select_backend` and `self._extract_embeddings` 
- Add the docstring for those methods to the prompt for the `fit_transform` method.

## Workflow

The default [pipeline](examples/run_code_annotation.py) executes the following steps:

1. Clone the repository from a remote URL (optional).
2. Parse all Python files from the repository's root directory.
3. Organize Python files by their import structure for dependency-aware processing.
4. Annotate each Python file's classes, functions, and methods, incorporating previous annotations as context.
5. Copy the annotated content into `new_repository_path`.

### Customization Options

- Choose between different LLMs (currently supports OpenAI or locally hosted TGI models).
- Customize the LLM prompt.
- Specify which files to annotate using a custom filter function.
- Configure the metadata for annotations.
- Determine how the LLM output is saved (e.g., as docstrings, comments).

Advanced customizations can be implemented by extending the provided pipeline classes.

## Command-Line Interface

The pipeline is also executable via command line. For available options, execute:

```bash
python run_code_annotation_command_line.py --help
```

## Possible Additional Use-Cases

The pipeline is designed for flexibility and can be adapted for various use cases, such as:

- RAG search using docstrings for embedding retrieval.
- Code understanding for LLM Agents.
- Generating knowledge graphs from code repositories.
- Producing README files using collective code annotations.

## Limitations:

Python is a dynamically typed language, and the codebase may thus contain dependencies that are difficult to resolve.
As an example, the code may have functions that call each other in a circular/recursive manner without the imports being
cyclic, or this being an actual bug.

Thus, not all functions/classes/methods may be ordered correctly in the pipeline and some functions may depend on
other functions/classes/methods that are either not annotated yet or have not been detected as dependencies.
If a function depends on another function that has not been annotated yet, this dependency will not be used when
creating the prompt for the LLM.

This repo uses [code2flow](https://github.com/scottrogowski/code2flow) to create the hierarchical code dependency structure.
`code2flow` has some limitations that will thus also apply here:

- If you use `def run_eval(model: torch.nn.Module, dataloader):` in a file, the `model` attribute may not
be associated as being an instance of your user-defined class `MyModel(nn.Module)` that you defined in another file.
- If you use `__init__.py` files to create import shortcuts, the pipeline may not be able to resolve the correct import.
- If you use `from . import my_module` in a file, the pipeline may not be able to resolve the correct import.
- Huge codebases may take very long to order by dependencies.

You can inspect the code dependency graph by running `examples/draw_dependency_graph.py` or running the `code2flow` command
directly in the terminal against your repository.

## FAQ/Troubleshooting:

### 1) Can I test the workflow without LLM model calls?

Yes, use `debug` pipeline for cost-free testing and debugging.
The annotated python files contain information about the import dependencies which is useful to test the pipeline.

### 2) Can I run this completely locally?

Absolutely, use `TGI` to deploy LLMs locally, then use `LocalTGILLM`.
Please ensure to remove the llm database if you test different models, as the caching database doesn't know about any
TGI inference changes.
Also, you may want to create a custom prompt template (see `LocalTGILLM` class) to account for the system prompt.

### 3) What is the annotation quality?

GPT-4 annotations are generally quite satisfying. For other models, you may need to tweak the prompt or shorten the
metainformation.

### 4) Can I view the prompts sent to the LLM?

Yes, check the LLM sqlite Database in the project's root folder,
e.g. `~/.cache/llm_docstring_generator/llm_docstring_generator_project/llm_cache_gpt-4-0125-preview/llm_cache.db`.

### 5) The code execution hangs?

OpenAI client connection may hang from time to time. Just restart the process; previous annotations are cached from the
database.

### 6) What are the expected annotation cost?

Current annotation costs for this repository are around 115K input tokens and 37K output tokens.
With current OpenAI's pricing (`gpt-4-0125-preview $10.00 / 1M tokens $30.00 / 1M tokens` as of April 2024),
this would cost around $2.26. The cost can be reduced by using gpt-3.5-turbo models and/or reducing the prompt size.
You can run `debug` LLM pipeline first to get a (rough) cost estimate in terms of tokens expected.

### 7) Will original docstrings be deleted?

No, the pipeline will not delete original docstrings. It will add the new docstrings alongside the original ones.


## Installation:

To be able to use the package from source, clone the repository and install the dependencies:

### Create a Virtual Environment (pipenv)

This is the recommended way to install the dependencies.
To create a virtual environment and install dependencies using pipenv:

```bash
sudo apt-get update && sudo apt-get install -y python3.10-dev graphviz libgraphviz-dev pkg-config
make setup
```

### Using requirements.txt

Alternatively, for conda or other virtual environments, dependencies can be installed from the `requirements.txt` file:
Please replace `python3.10-dev` with your Python version (development uses and tests on Python 3.10)

```bash
sudo apt-get update && sudo apt-get install -y python3.10-dev graphviz libgraphviz-dev pkg-config
pip install -r requirements.txt
```

## Similar Projects:

Here's an (incomplete) list of similar projects:

- https://github.com/MichaelisTrofficus/gpt4docstrings
- https://github.com/fynnfluegge/doc-comments-ai (supports multiple languages)
- https://github.com/context-labs/autodoc
- https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring (Visual Studio plugin)
- https://github.com/parthsarthi03/raptor (utilizes recursive clustering for RAG annotations)
- https://github.com/topoteretes/cognee (knowledge graph generation for natural language documents)

For additions, please submit an issue, and we will update the list.

## Disclaimer:

Utilizing this repository may incur costs from external API calls, such as OpenAI. It's advisable to use `DebugLLM` for
testing and cost estimation. The displayed token count in logs is approximate and may not accurately reflect costs. 
No liability is accepted for any costs related to usage of APIs such as OpenAI.
