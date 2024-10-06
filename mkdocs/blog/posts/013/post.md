---
date: 2024-06-22
categories:
  - examples
---

# Introducing `BunchStore`: A `Bunch` with Persistency

The `BunchStore` class serves as a straightforward key-value store, mapping a `Bunch` object seamlessly across both memory and the filesystem. It is particularly useful for caching API responses, utilizing its dictionary-like interface for easy data access and storage. Its file-based persistence guarantees data continuity across sessions.

!!! Tip
    The [DATAPAK](../../../advanced/storage.md) storage format used for serialization supports a wide range of complex data types.
    You can store text, images, dictionaries, lists, sets, arrays, dataframes, and more.

{{include_code("mkdocs/blog/posts/013/bunchstore.py", title="`BunchStore` example", drop_comments=False)}}

