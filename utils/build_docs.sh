#!/bin/sh

pip install --upgrade pip
pip install wheel
pip install mkdocs mkdocs-material mkdocs-macros-plugin pymdown-extensions mdx_include mkdocstrings
pip install mltraq --ignore-requires-python
mkdocs build