import subprocess


def local(args):
    cmd = " ".join(args) if type(args) == list else args
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode("utf-8")


def update_code_blocks():
    output = local("python utils/build_docs.py")
    assert "Operation completed" in output


def test_mkdocs():
    update_code_blocks()
    assert "Aborted" not in local("mkdocs build --strict")
