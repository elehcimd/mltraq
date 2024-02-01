from enum import StrEnum
from typing import Union

# Enum used with if-then situation with insertions
IfExists = StrEnum("IfExists", ["replace", "fail"])

# Enum used with if-then situations with deletions
IfMissing = StrEnum("IfMissing", ["ignore", "fail"])


def enforce_enum(x: Union[str, StrEnum], enum_type: StrEnum) -> StrEnum:
    """
    Convert string `x` to an enum value for type `enum_type`, or do nothing in case of enums.
    An invalid value results in a raised exception.
    """
    if isinstance(x, str):
        return enum_type[x]
    else:
        return x
