import numpy as np
from mltraq.opts import options
from mltraq.storage.serialization import deserialize
from mltraq.utils.bunch import BunchStore
from mltraq.utils.fs import tmpdir_ctx

with tmpdir_ctx():

    # Default location of BunchStore on filesystem
    print("Pathname:", options().get("bunchstore.pathname"))

    # Initialize object, creating file
    bs = BunchStore()
    bs["A"] = 123
    bs["B"] = np.array([4, 5, 6])

    # Reinitialize object object, reloading file
    bs = BunchStore()
    bs["C"] = 789

    # Accessing previouslty stored valued
    print("bs.A:", bs.A)

    data = deserialize(open(options().get("bunchstore.pathname"), "rb").read())
    print(f"File contents: {data}")