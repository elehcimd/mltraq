from enum import Enum
from typing import Union

# Enum used with if-then situation with insertions
IfExists = Enum("IfExists", ["replace", "fail"])

# Enum used with if-then situations with deletions
IfMissing = Enum("IfMissing", ["ignore", "fail"])


def enforce_enum(x: Union[str, Enum], enum_type: Enum) -> Enum:
    """Convert strings to enums, or do nothing in case of enums.

    Args:
        x (Union[str, Enum]): Object to convert.
        enum_type (Enum): Enum type to consider.

    Returns:
        Enum: Converted input object.
    """
    if type(x) == str:
        return enum_type[x]
    else:
        return x
