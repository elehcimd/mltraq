import pickle

import pytest

from mltraq.storage.serializers.pickle import PickleSerializer, UnsafePickle


def unsafe_func():
    # Example of unsafe access to globals, that might execute malicious code.
    return 1


def test_safe():
    """
    Test: We can safely unpickle simple dictionaries.
    """
    # Test that we can unpickle a simple dictionary with a string/int key/value.
    data = pickle.dumps({"a": 123})
    PickleSerializer.assert_safe(data)


def test_unsafe():
    """
    Test: We cannot unpickle unsafe objects. Not allowed opcode being used: STACK_GLOBAL
    """
    data = pickle.dumps({"a": unsafe_func})
    with pytest.raises(UnsafePickle):
        PickleSerializer.assert_safe(data)
