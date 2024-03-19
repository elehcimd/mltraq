import glob
from os import mkdir

import pandas as pd
from mltraq import create_session
from mltraq.storage.archivestore import ArchiveStore
from mltraq.utils.fs import tmpdir_ctx

with tmpdir_ctx():
    # Work in a temporary directory

    # Create a directory with two files
    mkdir("datasets")
    pd.Series([1, 2, 3]).to_csv("datasets/first.csv")
    pd.Series([4, 5, 6]).to_csv("datasets/second.csv")

    # Create an experiment
    s = create_session()
    e = s.create_experiment("test")

    # Define an archive (no tar file created!)
    e.fields.archived = ArchiveStore(src_dir="datasets", arc_dir="e")

    # Persist the experiment, creating the tar file
    e.persist()

    # Load the experiment, unarchiving the tar file
    e = s.load("test")

    print(f"Destination directory: '{e.fields.archived.get_target()}'")

    # Print contents of current directory
    print("Contents of current directory:")
    for idx, name in enumerate(glob.glob("**", root_dir=".", recursive=True)):
        print(f"[{idx:2d}] {name}")
