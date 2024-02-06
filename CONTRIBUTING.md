# Contributing

Thank you for considering contributing to MLtraq! MLtraq is an actively maintained and constantly improved project that serves a diverse user base with varying backgrounds and needs. This document will guide you through the process of contributing to the project.

## Getting started

To get started, follow these steps:

1. Fork the [mltraq](https://github.com/elehcimd/mltraq) repository and clone it to your local machine.
2. Install  [poetry](https://python-poetry.org/docs/#installation).
3. Create a Python virtual environment.
    
    ```
    # On MacOS:
    pyenv virtualenv 3.11.6 mltraq-dev
    pyenv local mltraq-dev
    pyenv activate mltraq-dev
    poetry env use $(which python)
    poetry install --all-extras --sync
    ```
4. Install the dependencies:

    ```
    poetry install --all-extras --sync
    ```    
4. Run the tests: 

    ```
    poetry run pytest
    ```


