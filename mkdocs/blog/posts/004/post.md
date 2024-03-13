---
date: 2024-03-13
categories:
  - examples
---

# Logging the code of steps

You can log the code and the parameters of the executed `steps` by turning on the `codelog` feature.
In the example below, we execute and log the code, location, and runtime parameters of a step function `init_fields`.

{{include_code("mkdocs/blog/posts/004/codelog.py", title="Tracking steps code", drop_comments=False)}}

!!! Question "Why are two steps being logged, and not just one?"
    The `MLtraq` executor implicitly calls the function `step_chdir` at step `#0` if the joblib backend is `loky`, to ensure 
    that the steps running in the pool worker processes have their current directory aligned with the primary process.
    This behavior is managed by the option `"execution.loky_chdir"`.
    
    The pool of worker processes is reused if multiple executions are triggered closely in time to increase efficiency (creating new processes is an expensive task for the operating system), but this means that they leak, and have the memory of, previously executed jobs.

    Besides being a security issue, this can also break your experiments if you use `chdir` in your steps.
    The implicit step `#0` resolves this issue.
