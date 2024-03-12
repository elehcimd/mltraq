---
date: 2024-03-12
categories:
  - examples
---

# Merging experiment runs

You don't always know all the parameters and variants you will evaluate upfront,
or executing each run takes so much time you prefer to split the experiment into smaller ones.

In these cases, merging experiments and unifying their analysis is desirable.
That's what we do in this example, merging experiments `e1` and `e2` into `e12`.

As we merge runs from different experiments, their runs might not be aligned anymore.
E.g., a run has a field named `a` but not `b`, and vice versa.
Instead, field `c` is available in both runs.
It is up to you to make sure that runs play well together.

!!! Tip
    The `runs` attribute of `Experiment` objects is a specialized dictionary with run IDs as keys and `Run` objects as 
    values. You can iterate, add, and remove runs with regular `dict` operations.


{{include_code("mkdocs/blog/posts/003/merge_runs.py", title="Union of runs", drop_comments=False)}}
