---
date: 2024-06-18
categories:
  - examples
---

# Automated Monitoring for Non-Finite Values in Arrays

When experimenting, it's important to ensure that your arrays meet certain criteria, such as containing no NaNs.
This can be easily achieved by using `BunchEvent` objects, as demonstrated in this example.

!!! Tip
    You can utilize `BunchEvent` objects to store arrays and various other data types during your experiments. Event handlers can trigger exceptions, which aids in streamlining the debugging process. In a production environment, replacing exceptions with notifications allows for proactive monitoring of both inference and training pipelines.

{{include_code("mkdocs/blog/posts/010/bunchevent.py", title="Automated monitoring for non-finite values in arrays", drop_comments=False)}}

