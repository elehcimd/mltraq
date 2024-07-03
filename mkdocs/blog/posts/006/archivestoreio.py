from os import mkdir

import pandas as pd
from mltraq.opts import options
from mltraq.storage.archivestore import ArchiveStoreIO
from mltraq.utils.fs import glob, tmpdir_ctx

with tmpdir_ctx():
    # Work in a temporary directory

    # Create a directory with two files
    mkdir("datasets")
    pd.Series([1, 2, 3]).to_csv("datasets/first.csv")
    pd.Series([4, 5, 6]).to_csv("datasets/second.csv")

    with options().ctx({"datastore.relative_path_prefix": "archives", "archivestore.relative_path_prefix": "all"}):

        # Create an archive and extract it
        archive = ArchiveStoreIO.create(src_dir="datasets", arc_dir="assets")
        archive.extract()

    # Print contents of current directory
    print("Contents of current directory:")
    for idx, name in enumerate(glob("**", root_dir=".", recursive=True)):
        print(f"[{idx:2d}] {name}")
