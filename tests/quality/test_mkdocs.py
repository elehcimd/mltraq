import os
import subprocess

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir + os.sep + os.pardir)


def local(args):
    """
    Execute local command, `args` is either a list to concatenate or a string.
    """
    cmd = " ".join(args) if isinstance(args, list) else args
    return subprocess.check_output(cmd, shell=True).decode("utf-8")  # noqa: S602


def test_update_code_blocks():
    """
    Test: We can regenerate the examples in the documentation with no errors.
    """
    output = local(f"python {PROJECT_DIR}/utils/build_docs.py")
    assert "Operation completed" in output


def test_mkdocs():
    """
    Test: We can generate the documentation with no errors.
    """
    assert "Aborted" not in local("mkdocs build --strict")
