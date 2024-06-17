---
date: 2024-04-15
categories:
  - examples
---

# Serializing a bunch of things

Sometimes, you want to serialize and deserialize a Python dictionary easily.
This is the perfect job for the [serialization API](https://mltraq.com/advanced/storage).
In the following example, we rely on the `Bunch` class as a dictionary container for a few fields.

{{include_code("mkdocs/blog/posts/009/serialization.py", title="Serializing a bunch of things", drop_comments=False)}}
