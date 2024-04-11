---
date: 2024-04-08
categories:
  - examples
---

# Upstreaming experimental results

With MLtraq, upstreaming results is as easy as persisting the experiment to a new session. You can use any SQL database supported by [SQLAlchemy](https://www.sqlalchemy.org/). No need to add more complexity with more dedicated running services.

{{include_code("mkdocs/blog/posts/008/upstream.py", title="Upstreaming experiments", drop_comments=False)}}
