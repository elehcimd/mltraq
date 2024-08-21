from mltraq.utils.fs import tmpdir_ctx
from mltraq.utils.web import fetch


def test_fetch_localfile():
    """
    Test: We can fetch a local file.
    """

    with tmpdir_ctx():
        with open("some.data", "wb") as f:
            f.write(b"0123456789")

        meta = fetch("file://some.data")
        assert open(meta.pathname, "rb").read() == b"0123456789"
