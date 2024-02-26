# State storage


The state of experiments is persisted to database using the method `Experiment.persist(...)` in two tables, `"experiments"` and `"experiment_{name}"` where `name` is the sanitized name of the experiment. In this section, we cover the database schema, the compression and the serialization methods.

!!! Tip
    The default table names can be changed via [options](./options.md).


## List of supported types

There are four classes of Python object types that can be persisted to database:

* `NATIVE_DATABASE_TYPES`: The values are stored as columns with native database types
* `BASIC_TYPES`: Serialized with DATAPAK format, stored in `LargeBinary` column
* `CONTAINER_TYPES`: Serialized with DATAPAK format, stored in `LargeBinary` column
* `COMPLEX_TYPES`: Serialized with DATAPAK format, stored in `LargeBinary` column

{{include_code("mkdocs/advanced/examples/storage-01.py", title="Supported types for database storage", 
drop_comments=False)}}

!!! Tip
    * Types in `NATIVE_DATABASE_TYPES` and `BASIC_TYPES` overlap. E.g., `int`. Whenever possible, native database types are used.
    * For fields with type in `NATIVE_DATABASE_TYPES`, there is no serialization, native SQL column types are used instead to maximize accessibility and enable SQL interoperability. The translation is handled using some of the [generic SQLAlchemy types](https://docs.sqlalchemy.org/en/20/core/type_basics.html#generic-camelcase-types).
    * Safe objects like `numpy.int32` or `datetime.date` cannot be part of `BASIC_TYPES` as they 
    depend on the `REDUCE` Pickle opcode, which is generally dangerous and unsafe.
    * The class `mltraq.utils.bunch.Bunch` is an ordered dictionary that mimics how[`sklearn.utils.Bunch`](https://scikit-learn.org/stable/modules/generated/sklearn.utils.Bunch.html) works: It extends dictionaries by enabling values to be accessed by key, `bunch["value_key"]`, or by an attribute, `bunch.value_key`.
    * The class `mltraq.storage.datastore.DataStore` extends `Bunch` and its values are stored separately, as defined by the datastore strategy. At the moment, the only datastore option is the filesystem. The datastore is recommended to store large objects to limit the size of the database.
    * The class `mltraq.utils.sequence.Sequence` models a multidimensional time series, with `append` and access as a Pandas dataframe.

## Persisting complex objects

In the next example, we persist and reload an experiment with a Numpy array:

{{include_code("mkdocs/advanced/examples/storage-02.py", title="Persistence for Numpy arrays", drop_comments=False)}}

## The DATAPAK format

The procedure to serialize and deserialize the types `BASIC_TYPES`, `CONTAINER_TYPES` and `COMPLEX_TYPES` is named **DATAPAK** and specifies how existing open formats are used together.

### Specification

#### Serialization

* Python types listed in `BASIC_TYPES` and `CONTAINER_TYPES` are serialized with the [Python pickle library](https://docs.python.org/3/library/pickle.html), allowing only a subset of safe Pickle opcodes.

* Python types listed in  `COMPLEX_TYPES` are encoded as regular Python `dict` objects with one element: the key (type: `str`) specified the type of the encoded object and the value (type: `bytes`) represents the encoded object.  

    An encoded complex type uses `CONTAINER_TYPES` and `BASIC_TYPES`, and it can be serialized with Pickle. The `COMPLEX_TYPES` types can be nested inside `CONTAINER_TYPES` types.

    The encoding of complex objects relies on open formats:

    * [Arrow IPC format](https://arrow.apache.org/docs/python/ipc.html) for Pandas and Arrow tables
    * [Numpy NEP format](https://github.com/numpy/numpy/blob/main/doc/neps/nep-0001-npy-format.rst) for Numpy arrays

If requested, the resulting binary blob is compressed (see separate section on this).

#### Deserialization

The deserialization applies the inverse procedure of the serialization:

1. Given a binary blob `A`, we decompress it, obtaining `B`. If the blob was not compressed, `A == B`.
2. `B` is by definition a **pickled Python object** we can safely unpickle, obtaining `C`. 
    3. If the type of `C` is in `BASIC_TYPES`, the deserialization is complete and we return `C`.
    4. If `C` is a `dict` that contains the DATAPAK magic key, we decode it, obtaining and returning `D`.
    5. Otherwise, if `C` is any of the `CONTAINER_TYPES` types, we decode it recursively, obtaining and returning `D`.
    6. If an unknown type is encountered, an exception is raised.

### Compression

Compression is optional and its behaviour is controlled via [options](./options.md).
By default, the compression is disabled and ["`zlib`"](https://docs.python.org/3/library/zlib.html) can be specified.
If enabled, the serialized object of type `bytes` is prefixed by a magic string that specifies the compression algorithm:

{{include_code("mkdocs/advanced/examples/storage-03.py", title="Supported compression codecs", 
drop_comments=False)}}

The decompression is transparent.
If any matching magic prefix is found, the decompression is attempted, returning the input if it fails.

### Example

In this example, we demonstrate how to manually deserialize an experiment field queried from database and containing a Numpy array.

1. Decompression: The first two bytes contain `b'C1'` (zlib compression)
2. Depickling: Complex objects are represented as dictionaries with one key/value pair that describe their encoded contents.
3. Safe loading of NumPy arrays, without trusting potentially harmful pickled objects.

{{include_code("mkdocs/advanced/examples/storage-04.py", title="Example of DATAPAK manual deserialization", drop_comments=False)}}

## Handling of unsupported types

If we need a type not currently supported, we can always encode/decode to field of type `bytes`,
which is supported. If we try to serialize unsupported types, an exception is raised:

{{include_code("mkdocs/advanced/examples/storage-05.py", title="Handling of unsupported types", drop_comments=False)}}

## Storing large artifacts

The [Datastore](./datastore.md) interface is designed to facilitate the storage and reloading of large objects such as datasets, weights and models. See its separate article for a comprehensive discussion.

## Unsafe pickling

It is possible, but not advised, to pickle/unpickle complete Experiment objects.

!!! Success "Safe with limitations"
    This procedure is safe if experiments are produced, stored and reloaded locally.
    It is generally much faster than trying to store the state in a controlled way.
    However, changes in the environment (architecture/package versions) might result
    in broken reloads and data loss, making it unsuitable for long-term storage.

In the following, we demonstrate how an unsafe object can be stored, pickled and unpickled in the `run.state` dictionary. The `run.steps` dictionary is always safeguarded form unsafe objects, and cannot be used.

!!! Danger
    Upon loading the experiment from database, the method `SomethingUnsafe.__setstate__` is evaluated as part of the unpickling procedure, with potential harmful instructions.

{{include_code("mkdocs/advanced/examples/storage-06.py", title="Unsafe unpickling", drop_comments=False)}}

!!! Info
    The serialization format and more details on the persistence logic are presented in more detail at [State storage](../advanced/storage.md).


## Database schema

Experiments are persisted on two tables:

### Table `"experiments"`

* `id_experiment`: UUID of the experiment
* `name`: Name of the experiment, by default a 6-alphanum hash of `id_experiment`
* `meta`: Serialized dictionary with properties on experiment and `runs` columns
* `fields`: Experiment `fields` as set by the user
* `unsafe_pickle`: Pickled `Experiment` object, disabled by default

### Tables `"experiment_xyz"`

Each experiment is associated to a dedicated table, ending with its sanitized name. E.g., `"experiment_xyz"` if `name=="xyz"`. There are only two fixed columns:

* `id_experiment`: UUID of the experiment
* `id_run`: UUID of the run

Additional columns are named as the keys in the `run.fields` dictionary present in all runs of the experiment.
Each row represents a `run` of the experiment.

Columns either use the native database SQL type, or DATAPAK.

!!! Tip
    In case of experiments persisted with `experiment.persist(store_unsafe_pickle=True)` and loaded with `experiment.load(unsafe_pickle=True)`, the experiment is also persisted as a binary blob which is unpickled upon loading (including its runs). Having the pickled blob does not limit/interfere with the regular storage semantics: the `fields` column in the `experiments` table, as well as the individual `experiment` tables, continue to operate as expected, and does not depend on the pickled object. This guarantees an extra level of interoperability and accessibility for the `fields` dictionaries.


