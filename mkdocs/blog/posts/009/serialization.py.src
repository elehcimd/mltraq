import numpy as np
from mltraq import Bunch
from mltraq.storage.serialization import deserialize, serialize

# Build a dictionary whose elements can be accessed as object attributes.
bunch = Bunch(a=np.array([1, 2, 3]), b="something")
bunch.c = 456

# Print its serialized binary blob (`bytes`)
print("Serialized", serialize(bunch)[:30])

# Demonstrate its deserialization
print("Deserialized", deserialize(serialize(bunch)))
