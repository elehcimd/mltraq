from common import execute


def main():

    execute("pytest --cov=src/mltraq tests/")
    execute("coverage report > coverage.txt")


if __name__ == "__main__":
    main()
