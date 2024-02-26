import abc
import zlib
from enum import Enum

from mltraq.opts import options
from mltraq.utils.bunch import Bunch
from mltraq.utils.exceptions import ExceptionWithMessage, InvalidInput


class UnsupportedCompressionCodec(ExceptionWithMessage):
    """
    Raised if an unsupported compression codec is requested.
    """

    pass


# Enum of supported codecs.
CompressionCodec = Enum("CompressionCodec", ["uncompressed", "zlib"])


# Compression prefixes.
MAGIC_COMPRESSION_PREFIX = {
    CompressionCodec.uncompressed: b"C0",
    CompressionCodec.zlib: b"C1",
}

# Inverse map, used for lookups at decompression.
MAGIC_COMPRESSION_PREFIX_MAP = {v: k for k, v in MAGIC_COMPRESSION_PREFIX.items()}


class Serializer(abc.ABC):
    """
    Abstract class for serializers.
    """

    @abc.abstractclassmethod
    def name(cls) -> str:
        """
        Return unique name/version of the serializer.
        """
        pass

    @abc.abstractclassmethod
    def serialize(cls, obj: object, **kwargs) -> bytes:
        return

    @abc.abstractclassmethod
    def deserialize(cls, data: bytes) -> object:
        pass

    @classmethod
    def meta(cls) -> Bunch:
        """
        Metadata about serializer configuration.
        """
        return Bunch(
            name=cls.name(),
            compression_codec=options().get("serialization.compression.codec"),
        )

    @classmethod
    def compress(cls, data: bytes) -> object:
        """
        Compress `data`.
        """

        # Make sure that we compress bytes
        if not isinstance(data, bytes):
            raise InvalidInput("You can compress only type `bytes`.")

        codec = CompressionCodec[options().get("serialization.compression.codec")]
        if codec == CompressionCodec.uncompressed:
            return data
        elif codec == CompressionCodec.zlib:
            return MAGIC_COMPRESSION_PREFIX[CompressionCodec.zlib] + zlib.compress(data)
        else:
            raise UnsupportedCompressionCodec(f"Codec not supported: '{codec}'")

    @classmethod
    def decompress(cls, data: bytes) -> bytes:
        """
        Try to decompress `data`, or return the original value
        if the decompression procedure fails.
        """

        codec = MAGIC_COMPRESSION_PREFIX_MAP.get(data[:2], CompressionCodec.uncompressed)

        # If uncompressed (magic prefix not found), return `data`.
        # If compressed, attempt to decompress.
        # if decompression fails, as we might have been unlucky with the magic compression prefix, return `data`.
        if codec == CompressionCodec.uncompressed:
            return data
        elif codec == CompressionCodec.zlib:
            try:
                return zlib.decompress(data[2:])
            except zlib.error:
                return data
        else:
            raise UnsupportedCompressionCodec(f"Codec not supported: '{codec}'")
