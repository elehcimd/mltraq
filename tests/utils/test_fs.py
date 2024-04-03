import os

from mltraq.utils.fs import globs, tmpdir_ctx


def create_test_file(pathname, content="something"):
    with open(pathname, "w") as f:
        f.write(content)


def create_test_dir():
    os.makedirs("test/a", exist_ok=True)
    os.makedirs("test/b", exist_ok=True)
    os.makedirs("test/.hidden", exist_ok=True)
    create_test_file("test/a/a1.x")
    create_test_file("test/a/a2.y")
    create_test_file("test/b/b1.z")
    create_test_file("test/b/c1.z")
    create_test_file("test/b/d")
    create_test_file("test/.hidden/h1.x")
    create_test_file("test/.h2.x")


def test_globs_default():
    """
    Test: We can retrieve the list of relative file names, recursively.
    """

    with tmpdir_ctx():
        create_test_dir()

        # Match all files but hidden ones
        names = globs("test")
        assert set(names) == {"a/a2.y", "b/b1.z", "a/a1.x", "b/d", "b/c1.z"}


def test_globs_hidden():
    """
    Test: We can include hidden files.
    """

    with tmpdir_ctx():
        create_test_dir()

        # Match also hidden files
        names = globs("test", include="*h2.x", include_hidden=True)
        assert names == [".h2.x"]


def test_globs_two_includes():
    """
    Test: We can specify two include patterns.
    """

    with tmpdir_ctx():
        create_test_dir()

        # Match also hidden files
        names = globs("test", include=["**/*a1*", "**/*a2*"])
        assert set(names) == {"a/a2.y", "a/a1.x"}


def test_globs_two_excludes():
    """
    Test: We can specify two exclude patterns.
    """

    with tmpdir_ctx():
        create_test_dir()

        # Match also hidden files
        names = globs("test", exclude=["**/*a1*", "**/*a2*"])
        assert set(names) == {"b/d", "b/b1.z", "b/c1.z"}
