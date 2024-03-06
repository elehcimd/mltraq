from pickletools import genops

import cloudpickle
from mltraq.storage.serializers.pickle_opcodes_whitelist import pickle_safe_opcodes_set
from mltraq.storage.serializers.serializer import Serializer
from mltraq.utils.exceptions import ExceptionWithMessage

# Pickle protocol version 5:
# Introduced with Python 3.8, https://peps.python.org/pep-0574/
# Unpickling might fail: on different architectures, different python version, in case of missing packages.
# In the simpler scenario of pickling a dictionary of bytes values (as in SerializerPYBIN), there are no issues.
PICKLE_DEFAULT_PROTOCOL = 5

# Version of the Pickle serializer
VERSION_SERIALIZER = "0.0"


class UnsafePickle(ExceptionWithMessage):
    """
    Raised if a potentially unsafe pickle ofcode is encountered.
    """

    pass


class PickleSerializer(Serializer):
    @classmethod
    def name(cls) -> str:
        return f"{cls.__name__}-{VERSION_SERIALIZER}"

    def assert_safe(pickle: bytes):
        """
        Make sure that it is safe to unpickle the object, by checking the opcodes defining it.
        No class/execution of code is allowed, only primitive types and containers (lists, dicts, tuples, sets).
        """

        pickle_opcodes = {opcode.name for opcode, arg, pos in genops(pickle)}
        unsafe_opcodes = pickle_opcodes - pickle_safe_opcodes_set
        if unsafe_opcodes:
            raise UnsafePickle(f"Encountered Pickle opcodes that might be unsafe: {unsafe_opcodes}, aborting.")

    @classmethod
    def serialize(cls, obj: object, assert_safe: bool = True) -> bytes:
        """
        Serialize object:
        1. Check safety of opcodes, if requested
        2. Pickle
        3. Compress, if requested
        """
        pickle = cloudpickle.dumps(obj, protocol=PICKLE_DEFAULT_PROTOCOL)
        if assert_safe:
            cls.assert_safe(pickle)
        return cls.compress(pickle)

    @classmethod
    def deserialize(cls, data: bytes, assert_safe: bool = True) -> object:
        """
        Deserialize bytes:
        1. Attempt decompress
        2. Check safety of opcodes
        3. Unpickle
        """
        pickle = cls.decompress(data)
        if assert_safe:
            cls.assert_safe(pickle)
        return cloudpickle.loads(pickle)
