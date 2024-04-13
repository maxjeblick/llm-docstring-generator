from llm_docstring_generator import run_code_graph_generation

repository_name = "llm_docstring_generator"
remote_url = "git@github.com:maxjeblick/llm-docstring-generator.git"

if __name__ == "__main__":
    run_code_graph_generation(
        repository_name=repository_name,
        remote_url=remote_url,
        mode="function_level",  # choose between "file_level" and "function_level"
        # FYI: pyvis has issues if the filename is not located in the current working directory
        graph_filename="./dependency_graph.html",
    )
