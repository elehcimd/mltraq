import numpy as np
from mltraq.utils.bunch import BunchEvent

# Instantiate a Bunch dictionary with event handlers
bunch = BunchEvent()


def alert_non_finite(key: str, value: np.ndarray):
    """
    Report the presence of non-finite values in array `value`
    """

    if not np.isfinite(value).all():
        print(f"Warning! key={key} contains non-finite values: {value}")
    else:
        print(f"All good! key={key} contains only finite values: {value}")


# Register event handler
bunch.on_setattr("predictions", alert_non_finite)

# Set an array with no nans (happy path)
print("Happy path")
bunch.predictions = np.array([0, 1, 2])
print("--\n")

# Set an array with nans (unexpected, there's a bug to fix)
print("Issue")
bunch.predictions = np.array([0, np.nan, 2])
print("--\n")
