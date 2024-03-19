---
date: 2024-03-14
categories:
  - examples
---

# Executing experiments with Ray

[Ray](https://docs.ray.io/en/latest/) is an open-source unified framework for scaling AI and Python applications.
You can use Ray as an execution backend to run `MLtraq` experiments using its native [joblib integration](https://docs.ray.io/en/latest/ray-more-libs/joblib.html).

The example shows how to set up a local Ray cluster, running an experiment with four workers.
The `1000` runs of the experiment are allocated to the `4` workers, `250` each.
The contents of the parameter `"execution.backend_params"` are passed as arguments to [`ray.init(...)`](https://docs.ray.io/en/latest/ray-core/api/doc/ray.init.html).

!!! Question "How can I install Ray?"
    You can [install](https://docs.ray.io/en/latest/ray-overview/installation.html) `Ray` with:
    ```
    pip install "ray[default]"
    ```


{{include_code("mkdocs/blog/posts/005/ray.py", title="Executing experiments with Ray", drop_comments=False)}}

