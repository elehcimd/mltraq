import glob
import os
import warnings

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir + os.sep + os.pardir)


def test_comments():
    """
    Test: Make sure that we don't forget about #fixme, #xxx,
    reporting a warning for each found pattern.
    """

    files = glob.glob(f"{PROJECT_DIR}/mkdocs/**/*.md", recursive=True)
    for d in ["src", "utils", "mkdocs", "tests"]:
        files += glob.glob(f"{PROJECT_DIR}/{d}/**/*.py", recursive=True)

    # Skip this test, which contains the patterns we're looking for.
    files = [file for file in files if not file.endswith("test_comments.py")]

    for file in files:
        data = open(file).read().lower()
        for pattern in ["xxx", "fixme"]:
            if pattern in data:
                warnings.warn(f"File {file} contains '{pattern}'", stacklevel=1)
