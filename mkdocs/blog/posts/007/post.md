---
date: 2024-04-03
categories:
  - examples
---

# In-memory archive files
Sometimes, serializing the contents of an entire directory as a `bytes` field in your experiment is a convenient way to share code and other small files across different environments.

The `Archive` interface simplifies the creation and extraction of in-memory TAR archives. The example below demonstrates 
how to archive a `src` directory, extracted to `src_archived`.

!!! Warning      
    Anything below 100 MB can easily fit in a field as a binary blob with `Archive`.
    We recommend to rely on the `DataStore` interface to persist and move larger archives.

{{include_code("mkdocs/blog/posts/007/archive.py", title="Archive example", drop_comments=False)}}
