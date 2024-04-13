from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="llm_docstring_generator",
    version="1.0",
    packages=find_packages(),
    description="Code to generate docstrings for Python code using GPT-4 etc.",
    author="Maximilian Jeblick",
    url="https://github.com/maxjeblick/llm-docstring-generator.git",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache-2.0 license",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=requirements,
)
