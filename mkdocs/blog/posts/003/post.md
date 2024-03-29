---
date: 2024-03-12
categories:
  - examples
---

# Merging experiments

You don't always know all the parameters and variants you will evaluate upfront,
or executing each run takes so much time you prefer to split the experiment into smaller ones.

In these cases, merging experiments and unifying their analysis is desirable.
That's what we do in this example, merging experiments `e1` and `e2` into `e12`.

!!! Warning
    As we merge runs from different experiments, their runs might not be aligned anymore.
    E.g., a run might have a field named `a` but not `b`, and vice versa.
    You are in charge of managing these differences.
   
!!! Tip
    * The `runs` attribute of `Experiment` objects is a specialized dictionary with run IDs as keys and `Run` objects as 
    values. You can iterate, add, and remove runs with regular `dict` operations.
    * You can use the `|` and `|=` operators directly on experiments to merge them: `e = e1 | e2`.

{{include_code("mkdocs/blog/posts/003/merge_runs.py", title="Union of runs", drop_comments=False)}}
