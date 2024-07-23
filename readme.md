# AST-Hints: Comparator and Hint Generator

## Comparator

The comparator is a tool that compares two ASTs.

## Hint Generator

The hint generator is a tool that generates hints for a given AST, calling OpenAI's API for use of the GPT-3.5 model and
the new GPT-4o-mini model.

## Command Line Interface

The command line interface is called astHint.
This is the primary entry point for the tool.
``
astHint --help
``
will show the available commands and options.

## Installation

First, install the required dependencies:
``
pip install -r requirements.txt
``
Ideally, in your favorite virtual environment.

Then, install the package:
``
pip install .
``
