# Adding experiments

Once you have established a session, you may want to create a new experiment, which is essentially a collection of runs that represent the experiment with different parameters. Let's start by defining an experiment with no runs:

{{include_code("mkdocs/tutorial/examples/add-experiment-001.py", title="Defining an experiment")}}

!!! Note "Experients and runs are identified by Universally Unique Lexicographically Sortable Identifiers (ULIDs)"

    * **Universal unique IDs**: Work on experiments locally, and then share them within the team once they are complete, copying them from a local database to a remote one; build multiple experiments and then consolidate the results by merging their runs into new experiments.
    * **IDs creation order == Lexicographical order**: Sorting experiments or runs by `SORT BY UUID ASC` will sort them by ascending order of creation.
    * **Compact 128-bit representation**: Databases with native `UUID` support (postgresql, cockroachdb, mssql) will benefit from greater performance in query evaluation and storage, falling back to `CHAR(32)` otherwise.
    
!!! Note "Tracking metadata about your experiments"
    * You can track data by either adding keyword arguments to `session.add_experiment` or by adding it directly to the `experiment.fields` dictionary.
    * Supported object types include: `dict`, `list`, `tuple`, `string`, `int`, `float`, `bool`, `pandas.Series`, `pandas.DataFrame`, `numpy.ndarray`, and `datetime64[ns]`.
    Upon saving the experiment to database, the fields are transparently serialised to and from SQL using a simple JSON format that can also be queried directly.

!!! Tip
    If you don't set explicitly a name for the experiment, a three-words hash of the UUID is used instead.
    For example, *"fire.gum.travel"*. You can set a name for the experiment passing the optional parameter `name`.

In the next example, we define an experiment tracking three objects: a `string`, a `pandas.Series` and a `pandas.DataFrame`. We persist and query it with the Python and SQL interfaces, showing also how to persist & load an experiment:

{{include_code("mkdocs/tutorial/examples/add-experiment-002.py", title="Defining an experiment")}}

!!! Note
    Fields are stored in `BINARY` columns to support their optional compression (zlib), disable by default.
    The serialization format is straightforward: native types are encoded using the 
    standard `json.dumps` procedure; custom types (such as Pandas objects) are 
    serialized by specifying their type and dumping their contents as native types.

