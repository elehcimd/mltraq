# Contributing

Thank you for considering contributing to MLtraq! MLtraq is an actively maintained and constantly improved project that serves a diverse user base with varying backgrounds and needs. This document will guide you through the process of contributing to the project.

## Discussions

Feel free to drop your thoughts and questions in the [Discussions](https://github.com/elehcimd/mltraq/discussions) - a place to connect with other members of our community.

## Getting started

To get started, follow these steps:

1. Fork the [mltraq](https://github.com/elehcimd/mltraq) repository and clone it to your local machine.
2. Install [poetry](https://python-poetry.org/docs/#installation) to manage dependencies and packaging.
3. Install virtual environment and dependencies:

    ```
    cd mltraq
    poetry install --all-extras --sync
    ```    
4. Run the tests:

    ```
    poetry run pytest
    ```


## Submitting changes

When you're ready to contribute, follow these steps:

1. Create an issue describing the feature, bug fix, or improvement you'd like to make.
2. Create a new branch in your forked repository for your changes.
3. Write your code and tests.
4. Test, format, and lint your code by running `pytest`.
6. Create a pull request targeting the `devel` branch of the main repository.

## Active branches

We use `devel` (which is our default Github branch) to prepare a next release of `mltraq`. We accept all regular contributions there (including most of the bugfixes).

We use `main` branch for hot fixes (including documentation) that needs to be released out of normal schedule.

On the release day, `devel` branch is merged into `main`. All releases of `mltraq` happen only from the `main`.

## Creating an environment on MacOS with a specific version of Python

```
pyenv versions # List Python versions and available environments
pyenv install 3.9:latest # Install Python version
poetry env use 3.9.18

```

### Adding a dev package

```
poetry add pytest@latest --group dev
```