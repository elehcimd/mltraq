import os
import subprocess
from typing import List, Union

project_dir = os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir)
project_name = os.path.basename(project_dir)


def local(args: Union[List[str], str]) -> str:
    cmd = " ".join(args) if isinstance(args, list) else args
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode("utf-8")  # noqa: S602


def execute(cmd: str):
    print(f"Executing: {cmd}")
    assert os.system(cmd) == 0  # noqa: S605


def get_package_version(pathname: str) -> str:
    section_match = False
    with open(pathname, "rb") as f:
        for line in f.readlines():
            line = line.decode("utf-8").strip()
            if line == "[tool.poetry]":
                section_match = True
            elif line.startswith("["):
                section_match = False
            elif section_match and line.startswith("version = "):
                version = line[10:].strip('"')
                return version
    return None


pkg_version = get_package_version(f"{project_dir}/pyproject.toml")
