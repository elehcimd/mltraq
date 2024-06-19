---
date: 2024-06-19
categories:
  - examples
---

# Streamline Debugging with Faster Issue Detection

The new execution option `return_as=generator_unordered` can be set via `options` to facilitate quicker issue detection in your runs. This feature allows you to identify and resolve failures without waiting for all executions to complete, enhancing the efficiency of diagnostics and debugging.

{{include_code("mkdocs/blog/posts/011/failfast.py", title="Streamline debugging with faster issue detection", drop_comments=False)}}

