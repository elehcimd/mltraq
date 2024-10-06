from mltraq.cli import main
from mltraq.version import __version__ as mltraq_version


def test_cli_version(capsys):
    """
    Test: We can execute "mltraq version" to get the version of the installed MLtraq package.
    """

    main(["version"])

    out = capsys.readouterr().out
    assert out == f"MLtraq v{mltraq_version}\n"
