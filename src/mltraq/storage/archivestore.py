from __future__ import annotations

import fnmatch
import glob
import logging
import os
import tarfile
from io import BytesIO
from os.path import normpath
from shutil import rmtree
from typing import BinaryIO

from mltraq.opts import options
from mltraq.storage.datastore import DataStoreIO
from mltraq.utils.bunch import Bunch
from mltraq.utils.exceptions import InvalidInput

log = logging.getLogger(__name__)


class Archive:
    """
    Creation of binary TAR binary blob archives and extraction to filesystem.
    """

    @classmethod
    def create(
        cls,
        src_dir: str,
        arc_dir: str = ".",
        include: str = "**",
        exclude: str | None = None,
        include_hidden=False,
    ) -> bytes:
        """
        Return a binary blob representing a TAR file.
        """

        buffer = BytesIO()

        ArchiveStoreIO.add_files(
            fileobj=buffer,
            src_dir=src_dir,
            arc_dir=arc_dir,
            include=include,
            exclude=exclude,
            include_hidden=include_hidden,
        )

        return buffer.getvalue()

    @classmethod
    def extract(cls, data: bytes, target: str = ".", members: list[str] | None = None):
        """
        Extracts the archive from the `data` binary blob to `target` directory.
        """

        log.debug(f"Extracting archive to '{target}' ...")

        buffer = BytesIO()
        buffer.write(data)
        buffer.seek(0)

        with tarfile.open(fileobj=buffer, mode="r") as archive:
            archive.extractall(target, members=members, filter="data")


class ArchiveStoreIO:
    """
    Handling of TAR files of directories.
    """

    # Attributes to store and serialize.
    __slots__ = "url"
    __state__ = ("url",)

    def __init__(self, url: str):
        """
        Create a new linked archive.
        """
        self.url = url

    @classmethod
    def add_files(
        cls,
        fileobj: BinaryIO,
        src_dir: str,
        arc_dir: str = ".",
        include: str = "**",
        exclude: str | None = None,
        include_hidden=False,
    ):
        """
        Add files to an open archive file `fileobj`, from directory `src_dir`, using archive directory `arc_dir`,
        including glob pattern `include`, excluding glob pattern `exclude`, honoring `include_hidden`.
        """

        if not os.path.isdir(src_dir):
            raise InvalidInput(f"Source directory '{src_dir}' does not exist")

        with tarfile.open(
            fileobj=fileobj, mode=options().get("archivestore.mode"), format=options().get("archivestore.format")
        ) as archive:

            for idx, glob_name in enumerate(
                glob.glob(include, root_dir=src_dir, recursive=True, include_hidden=include_hidden)
            ):
                name = normpath(src_dir + os.sep + glob_name)
                arcname = normpath(arc_dir + os.sep + glob_name)
                include_file = True

                if exclude is not None and fnmatch.fnmatch(name, exclude):
                    include_file = False

                info = archive.gettarinfo(name=name, arcname=arcname)
                if not info or not info.isreg():
                    # Not a regular file, skipping
                    include_file = False

                if not include_file:
                    log.debug(f"{cls.__name__}: [{idx}] Excluding {name}")
                    continue

                log.debug(f"{cls.__name__}: [{idx}] Adding {name} -> .../{arcname}")

                info.uid = 0
                info.gid = 0
                info.uname = "root"
                info.gname = "root"

                with open(name, "rb") as f:
                    archive.addfile(info, f)

    @classmethod
    def create(
        cls,
        src_dir: str,
        arc_dir: str = ".",
        include: str = "**",
        exclude: str | None = None,
        include_hidden=False,
    ) -> ArchiveStoreIO:
        """
        Creates and stores the archive, returning its ArchiveStoreIO representation.
        """

        pathname, url = DataStoreIO.get_next_pathname_url()
        # We use GNU format for increased portability, including tar on macos that
        # fails with the PAX default format.

        log.debug(f"{cls.__name__}: Creating archive {pathname}")
        with open(pathname, "xb") as f:
            cls.add_files(
                fileobj=f,
                src_dir=src_dir,
                arc_dir=arc_dir,
                include=include,
                exclude=exclude,
                include_hidden=include_hidden,
            )

        return ArchiveStoreIO(url)

    @classmethod
    def get_target(cls, target: str | None = None):
        """
        Get the target directory for the uncompressed TAR. If `target` is passed as
        a parameter, it is returned with no changes. If missing, it defaults to the
        concatenation of defaults for archivesture URL and relative path prefix.

        The target directory is passed as first argument to Tarfile.extractall(...).
        """

        if not target:
            target = (
                DataStoreIO.get_filepath(options().get("archivestore.url"))
                + os.sep
                + options().get("archivestore.relative_path_prefix")
            )
        return target

    def extract(self, target: str | None = None, members: list[str] | None = None) -> ArchiveStoreIO:
        """
        Extracts the archive to `target` directory.
        """

        target = ArchiveStoreIO.get_target(target)

        log.debug(f"Extracting archive to '{target}' ...")

        with self.open() as archive:
            # Data filter: https://docs.python.org/3.10/library/tarfile.html#tarfile.data_filter
            archive.extractall(target, members=members, filter="data")

        return self

    def getnames(self, target: str | None = None) -> list[str]:
        """
        Load archive and return a list with its archived file names.
        """

        target = ArchiveStoreIO.get_target(target)
        with self.open() as archive:
            return [normpath(target + os.sep + name) for name in archive.getnames()]

    def open(self):
        """
        Return the Tarfile object pointing to the archive URL.
        """
        return tarfile.open(DataStoreIO.get_pathname_from_url(self.url), mode="r")

    @classmethod
    def delete(cls, relative_path_prefix: str):
        """
        Delete directory `relative_path_prefix`, used to drop directory
        associated to an experiment being deleted.
        """
        pathdir = DataStoreIO.get_filepath(options().get("archivestore.url")) + os.sep + relative_path_prefix
        rmtree(pathdir, ignore_errors=True)


class ArchiveStore:

    __slot__ = ("params",)

    def __init__(
        self, src_dir: str, arc_dir: str = ".", include: str = "**", exclude: str | None = None, include_hidden=False
    ):
        """
        Lazily define an archive, without creating it.
        """

        self.params = Bunch(
            src_dir=src_dir, arc_dir=arc_dir, include=include, exclude=exclude, include_hidden=include_hidden
        )

    def to_url(self) -> str:
        """
        If the archive doesn't exist yet, create it.
        It returns the URL to the archive.
        """

        archive = ArchiveStoreIO.create(
            src_dir=self.params.src_dir,
            arc_dir=self.params.arc_dir,
            include=self.params.include,
            exclude=self.params.exclude,
            include_hidden=self.params.include_hidden,
        )
        return archive.url

    @staticmethod
    def from_url(url) -> ArchiveStore:
        """
        Extracts the archive from `url` and returns
        an ArchiveStore object pointing to it.
        """

        ArchiveStoreIO(url).extract()
        obj = ArchiveStore.__new__(ArchiveStore)
        obj.params = Bunch(target=ArchiveStoreIO.get_target())

        return obj

    def get_target(self) -> str | None:
        """
        Return the destination directory of the unarchived files
        """
        return self.params.get("target", None)
