import os
import subprocess

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir + os.sep + os.pardir)


def local(args):
    """
    Execute local command, `args` is either a list to concatenate or a string.
    """
    cmd = " ".join(args) if isinstance(args, list) else args
    return subprocess.check_output(cmd, shell=True).decode("utf-8")  # noqa


def test_ruff():
    """
    Test: lint/format code with ruff, and test it.
    """
    local(f"ruff check {PROJECT_DIR} --fix --exit-zero")
    assert local(f"ruff check {PROJECT_DIR} --exit-zero") == ""


def test_black():
    """
    Format code with Black.
    """
    local(f"black {PROJECT_DIR}")
