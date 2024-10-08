from os import mkdir

from mltraq import create_session
from mltraq.storage.archivestore import Archive
from mltraq.utils.fs import glob, tmpdir_ctx

with tmpdir_ctx():
    # Work in a temporary directory

    # Create a directory with a file
    mkdir("src")
    with open("src/simple_print.py", "w") as f:
        f.write("print(1 + 2)\n")

    # Create an experiment
    s = create_session()
    e = s.create_experiment("test")

    # Create the archive
    e.fields.src = Archive.create(src_dir="src", arc_dir="src_archived")

    # Persist the experiment, including the binary TAR blob
    e.persist()

    # Load the experiment
    e = s.load_experiment("test")

    # Extract the contents of the archive
    e.fields.src.extract()

    # Print contents of current directory
    print("Contents of current directory:")
    for idx, name in enumerate(glob("**", root_dir=".", recursive=True)):
        print(f"[{idx:2d}] {name}")
