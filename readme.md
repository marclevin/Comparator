# AST-Hints: Comparator and Hint Generator

## Comparator

The comparator is a tool that compares two ASTs.

## Hint Generator

The hint generator is a tool that generates hints for a given AST, calling OpenAI's API for use of the GPT-3.5 model and
the GPT-4o-mini model.

## Command Line Interface

The command line interface is called astHint.
This is the primary entry point for the tool.
``
astHint --help
``
will show the available commands and options.

## Installation

To install the CLI, clone the repository and run the following commands in the root directory:

1. Create & activate your favourite virtual environment.
   ```
   conda create -n ast-hints python=3.11
   conda activate ast-hints
   ```
2. Install AST-Hints as a package. (Editable mode, remove -e if you want to install it plainly)
   ```
   pip install -e .
   ```
3. Get an OpenAI API key and set it as an environment variable.
   ```
   export OPEN_AI_API_KEY=your_api_key
   ```
4. Run the CLI
   ```
   astHint --help
   ```

## Development

To develop the CLI, clone the repository and run the following commands in the root directory:

1. Create & activate your favourite virtual environment.
   ```
   conda create -n ast-hints python=3.11
   conda activate ast-hints
   ```
2. Add a `.env` file in the root directory with the following content:
   ```
   OPEN_AI_API_KEY=your_api_key
   ```
3. Install the requirements.
   ```
   pip install -r requirements.txt
   ```
4. Install AST-Hints as a package. (Editable mode, remove -e if you want to install it plainly)
   ```
   pip install -e .
   ```
5. Run the CLI
   ```
   astHint --help
   ```

### Testing

This project uses `unittest` for testing. Tests are located in the `tests` directory.

To run the tests, run the following command in the root directory:

```
python -m unittest discover tests
```

This project also uses `coverage` for code coverage. To run the tests and generate a coverage report, run the following
command in the root directory:

```
coverage run -m unittest discover tests
coverage report
```




