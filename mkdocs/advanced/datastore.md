# Data store

This interface lets you transparently store and load objects outside the data base.

## The DataStore class

The `DataStore` class is a dictionary whose values can also be accessed as object attributes.

Upon serialization, its contents are serialized to the filesystem (or somewhere else) and only an `url` reference is retained as its value. The object is deserialized by loading the contents referenced in the `url`.


There are no limits to how many objects you can store within a `DataStore` object and you can add as many `DataStore` objects as you want to `run.fields`.

!!! Info
    By default, the data store relies on the filesystem. The base directory is defined by [option](../advanced/options.md) `datastore.url`. The files are organized in subdirectories, named as experiment IDs.

!!! Warning "Important"
    If an experiment is deleted, its associated datastore folder is also removed.
    If an experiment is persisted, its associated datastore folder is wiped before using it.

!!! Question "Can I use third-party storage services?"
    Yes! The datastore interface is designed to be flexible. If you are interested in using more storage options, please request it on the [issue tracker](https://github.com/elehcimd/mltraq/issues) or [open a discussion](https://github.com/elehcimd/mltraq/discussions).

In the following, we demonstrate how to add two `DataStore` objects. Each `DataStore` object is serialized separately. Depending on the use case, you might want to increase storage efficiency by adding more
values to a single `DataStore`, resulting in I/O with a single reference.

{{include_code("mkdocs/advanced/examples/datastore-01.py", title="DataStore example", drop_comments=False)}}

## The DataStoreIO class

In some cases, you might need a more fine-grained control on how, when and where the objects are serialized and written. The class `DataStoreIO` comes to the rescue.

 In the following example, we show how to store directly two values. Value `a` is a `NumPy` array
and requires serialization. Value `b` is a `bytes` object and can be written directly skipping serialization (faster). The values are persisted regardless of the experiment, which is not persisted.

!!! Warning
    The value of `relative_path_prefix` must be different than the experiment ID. Why? Whenever the experiment
    is persisted with `experiment.persist()`, the contents of the experiment ID subdirectory are wiped, 
    consistently with the semantics of the class `DataStore`. With `DataStoreIO`, you are in charge of
    managing the files, including their deletion.

{{include_code("mkdocs/advanced/examples/datastore-02.py", title="DataStoreIO example", drop_comments=False)}}
