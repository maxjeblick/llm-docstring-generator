import fire
from llm_docstring_generator.pipelines.run_code_annotation_pipeline import (
    run_code_annotation_pipeline,
)

if __name__ == "__main__":
    fire.Fire(run_code_annotation_pipeline)
