import os

from mltraq import create_experiment
from mltraq.storage.archivestore import Archive, ArchiveStore, ArchiveStoreIO
from mltraq.utils.fs import tmpdir_ctx


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


def test_archive_cls():
    """
    Test: We can create and extract TAR binary blobs.
    """

    with tmpdir_ctx():
        create_test_dir()

        # Create ZIP
        archive = Archive.create("test")

        # Extract ZIP to ./test2/
        Archive.from_bytes(archive.to_bytes()).extract("test2")

        # Check presence or not of files
        assert os.path.isfile("test2/a/a1.x")
        assert not os.path.isfile("test2/.hidden/h1.x")


def test_archive_arcdir():
    """
    Test: We can set the destination directory via arc_dir.
    """

    with tmpdir_ctx():
        create_test_dir()
        a = ArchiveStoreIO.create(src_dir="test", arc_dir="x", include="**/a1.x")
        names = set(a.getnames())

        assert names == {"mltraq.archivestore/undefined/x/a/a1.x"}


def test_archive_include():
    """
    Test: We can include file patterns.
    """

    with tmpdir_ctx():
        create_test_dir()
        a = ArchiveStoreIO.create(src_dir="test", include="**/a1.x")
        names = set(a.getnames())

        assert names == {"mltraq.archivestore/undefined/a/a1.x"}


def test_archive_exclude():
    """
    Test: We can exclude file patterns.
    """

    with tmpdir_ctx():
        create_test_dir()
        a = ArchiveStoreIO.create(src_dir="test", exclude="**/a1.x")
        names = set(a.getnames())

        assert "mltraq.archivestore/undefined/a/a1.x" not in names


def test_archive_include_hidden():
    """
    Test: We can include hidden files.
    """

    with tmpdir_ctx():
        create_test_dir()
        a = ArchiveStoreIO.create(src_dir="test", include_hidden=True)

        names = set(a.getnames())

        assert "mltraq.archivestore/undefined/.hidden/h1.x" in names


def test_archive_simple():
    """
    Test: We can include all files, excluding hidden ones by default.
    """

    with tmpdir_ctx():
        create_test_dir()
        a = ArchiveStoreIO.create(src_dir="test")

        names = set(a.getnames())

        assert names == {
            "mltraq.archivestore/undefined/a/a1.x",
            "mltraq.archivestore/undefined/a/a2.y",
            "mltraq.archivestore/undefined/b/c1.z",
            "mltraq.archivestore/undefined/b/b1.z",
            "mltraq.archivestore/undefined/b/d",
        }


def test_archivestore():
    """
    Test: We can transparently handle an archived directory in experiments.
    """

    with tmpdir_ctx():

        # Create experiment
        create_test_dir()
        e = create_experiment()

        # Add archivestore for folder 'test' and persist experiment.
        e.fields.archive = ArchiveStore("test")
        e.persist()

        # Reload experiment, and verify that files have been unarchived in the experiment's folder.
        e.reload()
        assert os.path.exists(f"mltraq.archivestore/{str(e.id_experiment)}/a/a1.x")
