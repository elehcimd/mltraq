import glob
import os
import sys

from common import execute, project_dir


def main(argv):
    os.chdir(project_dir)

    if len(argv) > 1:
        pattern = argv[1]
        print(f"Limiting to files matching pattern '{pattern}'")
    else:
        pattern = ""

    notebook_pathnames = glob.glob(f"notebooks/**/*{pattern}*.ipynb", recursive=True)

    for notebook_pathname in notebook_pathnames:
        print(f"Processing {notebook_pathname}")
        execute(f"ruff notebooks --fix '{notebook_pathname}'")
        execute(f"black --line-length 75 '{notebook_pathname}'")
        execute(
            "PYDEVD_DISABLE_FILE_VALIDATION=1 jupyter nbconvert "
            f"--execute --to notebook --inplace '{notebook_pathname}'"
        )


if __name__ == "__main__":
    main(sys.argv)
