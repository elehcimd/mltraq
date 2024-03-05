---
date: 2024-03-06
categories:
  - examples
---

# Querying columns with native SQL types

The field values of experiments stored in SQL tables can be queried directly with SQL if they are among the ones that provide a native SQL type.
These include `bool`, `int`, `float`, `string`, `time`, `datetime`, `date`, `UUID`, and `bytes`.

!!! Question "Why should you care?"
    You can quickly build a reporting dashboard using your existing infrastructure (database and dashboard) at no added complexity/cost.

{{include_code("mkdocs/blog/posts/001/select_native_sql.py", title="Querying columns with native SQL types", drop_comments=False)}}
