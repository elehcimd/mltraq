# Options management

MLtraq manages global preferences with the object `mltraq.options`, whose class follows the Singleton pattern and is transparently replicated in read-only mode to other processes that handle the execution of `runs` with `step` functions.

Options are organized in a tree-like structure with values at their leaves and indexed by dot-separated strings. The data is stored as a nested Python dictionary. If the query string does not reach a leaf, a dictionary is returned, with the matching sub-tree.

## The options tree

!!! Example "Diagram of the options tree, query strings and returned values"


    ``` mermaid
    flowchart LR
    X(((Options)))
    
    X --> xa(a)
    xa --> ab(b) --> abc(c) --> v1[12]
    xa --> ad(d) --> v2['hello']
    X --> xe(e) --> v3["#123;'k':3#125;"]
    X --> xf(f)
    xf(f) --> xfg(g) --> v4[46]
    xf(f) --> xfh(h) --> v5[Object]

    style X stroke-width:3px
    style v1 stroke-width:3px
    style v2 stroke-width:3px    
    style v3 stroke-width:3px 
    style v4 stroke-width:3px
    style v5 stroke-width:3px
    ```

    --- 

    * `options.get("a.b.c")` returns the int `12`
    * `options.get("a.d")` returns the string `'hello'`
    * `options.get("e")` returns the dictionary `{'k':3}`
    * `options.get("f")` returns the dictionary `{'g': 46, 'h': Object}`

## Context manager

You can use the context manager `options.ctx` to temporarily modify the configuration.

{{include_code("mkdocs/advanced/examples/options-01.py", title="Using the context manager with options")}}

## Nesting options

You can define a new group of options extending the class `BaseOptions` defined in `mltraq.utils.base_options` and requesting its singleton instance. Options are stored in the `.options` attribute and can be nested to other existing option groups, as we demonstrate in the following example.

{{include_code("mkdocs/advanced/examples/options-03.py", title="Nesting options")}}


## Default options

### Overview
  
Listing the default values of the options. The generation of the documentation (which relies on the `options.ctx` context manager)  alters two values:

* `"tqdm.disable"` is set to `False` to improve readability in the docs.
* `"fake_incremental_uuids"` is set to `False` to avoid random UUIDs in the documentation.

{{include_code("mkdocs/advanced/examples/options-02.py", title="Default option values")}}

### Reference documentation

* The prefix `"app.*"` is reserved for the application, is empty by default, and can be used by the application to customize the behaviour of steps.

* Options `"database.*"` control the behaviour of the connection to the database, chunking, and table names/prefixes.
    * I/O operations are chunked by number of rows, `"database.query_read_chunk_size"` and `"database.query_write_chunk_size"`, to implement progress bar reporting.
    * If `"tqdm.disable"` is set to `False`, there is no chunking.
    * If `"database.ask_password"` is set to True, the password of the connection string is requested interactively.
    * `"database.echo"`, `"database.pool_pre_ping"`, `"database.url"` are passed to SQLAlchemy.
    * `"experiments_tablename"` defines the table name used to index the experiments and their meta data. `"experiment_tableprefix"` is the table prefix used for individual experiment tables.

* Options `"execution.*"` cover how experiments (and their runs) are execucted.
    * If `"execution.exceptions.compact_message"` is set to true, exceptions raised within runs are reported with a compact, friendly format. It might hide useful context to debug errors, so it's False by default.

* Options `"reproducibility.*"` handle outputs can be reproduced accurately.
    * The random seed of the Python `random` and `numpy` packages resets to `"reproducibility.random_seed"` before executing runs, ensuring reproducibility.
    * If `"reproducibility.fake_incremental_uuids"` is set to True, there is no randomness for UUIDs generated for experiments and run IDs, simplifying tests and avoiding unnecessary changes in the documentation.

* Options `"serialization.*` set defaults on compression and storage of experiments.

* Options `"tqdm.*`" are parameters passed to `tqdm` to render the progress bars used in the evaluation of `runs` and SQL queries.