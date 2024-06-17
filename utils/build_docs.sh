#!/bin/sh

# Regenerate docs website.

pip install --upgrade pip
pip install wheel
pip install mkdocs mkdocs-material mkdocs-macros-plugin pymdown-extensions mdx_include mkdocstrings mkdocs-charts-plugin
pip install mltraq --ignore-requires-python
mkdocs build
