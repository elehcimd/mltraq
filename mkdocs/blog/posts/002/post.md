---
date: 2024-03-07
categories:
  - examples
---

# The Fibonacci sequence

In mathematics, the Fibonacci sequence is a sequence in which each number is the sum of the two preceding ones, starting with `[0, 1]`.

Let's calculate the first ten values of the sequence with the `init_fields` step factory function to initialize the accumulator variable, using the `step` function to determine the next value in the sequence.

{{include_code("mkdocs/blog/posts/002/fibonacci.py", title="Fibonacci sequence", drop_comments=False)}}
