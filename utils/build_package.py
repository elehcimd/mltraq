import os

from common import execute, get_package_version, project_dir, project_name


def inc_version() -> str:
    execute("poetry version patch")

    pkg_version = get_package_version(f"{project_dir}/pyproject.toml")

    with open(f"{project_dir}/src/{project_name}/version.py", "w") as f:
        f.write(f'__version__ = "{pkg_version}"\n')

    return pkg_version


def pytest():
    execute("poetry run pytest")


def main():
    os.chdir(project_dir)
    pytest()
    pkg_version = inc_version()
    execute("poetry run python utils/build_badges.py")
    execute("poetry run python utils/svg_optimizer.py")
    execute("poetry build")
    print(f"Package {project_name} v{pkg_version} ready!")
    print('To publish:\n 1. $ poetry "-u$PYPI_USERNAME" "-p$PYPI_PASSWORD" --build publish\n 2. update repository')


if __name__ == "__main__":
    main()
