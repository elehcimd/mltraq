import glob

import numpy as np
import pandas as pd

from mltraq import DataStore, create_experiment
from mltraq.utils.fs import tmpdir_ctx

with tmpdir_ctx():

    # Create a new experiment and execute a run
    experiment = create_experiment()
    with experiment.run() as run:
        # DataStore with two values
        run.fields.ds = DataStore()
        run.fields.ds.a = np.zeros(10)
        run.fields.ds.b = pd.Series([1, 2, 3])

        # DataStore with a single value
        run.fields.ds2 = DataStore()
        run.fields.ds2.c = 123

    # Persist experiment
    experiment.persist()

    print(f"ID experiment: {experiment.id_experiment}")
    print("--\n")

    # List files in datastore directory
    print("Contents of datastore directory:\n")
    for pathname in glob.glob("*/**", recursive=True):
        print(pathname)
    print("--\n")

    # Reload experiment from database
    experiment.reload()

    # Show stored values
    ds = experiment.runs.first().fields.ds
    ds2 = experiment.runs.first().fields.ds2
    print("a", type(ds.a), ds.a)
    print("b", type(ds.b), ds.b.values)
    print("c", type(ds2.c), ds2.c)
