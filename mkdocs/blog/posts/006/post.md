---
date: 2024-03-19
categories:
  - examples
---

# Archive files


## ArchiveStore

The `ArchiveStore` interface lets you manage TAR archives transparently.
In the example below, the directory `datasets` is archived and stored as a regular `DataStore` asset.
Persisting the experiment triggers the creation of the archive.
Upon loading the experiment, the archive is extracted in the directory `mltraq.archivestore`,
organized similarly to `mltraq.datastore` by experiment ID.

!!! Warning
    Persisting an experiment is equivalent to removing and saving it, triggering the deletion
    and recreation of its associated datastore assets, including its archives.
    You can implement different behaviors with `ArchiveStoreIO` and `DataStoreIO`.

{{include_code("mkdocs/blog/posts/006/archivestore.py", title="ArchiveStore example", drop_comments=False)}}

## ArchiveStoreIO

The class `ArchiveStoreIO` provides a lower-level interface to manage archives, bypassing the
organization by experiment IDs. Its implementation
relies on the [`glob`](https://docs.python.org/3/library/glob.html) and [`tarfile`](https://docs.python.org/3/library/tarfile.html)
modules from the standard library. You can pass patterns to include or exclude and optionally include hidden files.

{{include_code("mkdocs/blog/posts/006/archivestoreio.py", title="ArchiveStoreIO example", drop_comments=False)}}
