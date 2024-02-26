from enum import Enum

from mltraq.utils.exceptions import InvalidInput

# Enum used with if-then situation with insertions/deletions
IfExists = Enum("IfExists", ["replace", "delete", "fail"])

# Enum used with if-then situations with deletions
IfMissing = Enum("IfMissing", ["ignore", "fail"])


def enforce_enum(x: str | Enum, enum_type: Enum) -> Enum:
    """
    Convert string `x` to an enum value for type `enum_type`, or do nothing in case of enums.
    An invalid value results in a raised exception.
    """
    if isinstance(x, str):
        return enum_type[x]
    elif isinstance(x, Enum):
        return x
    else:
        InvalidInput(f"Expected str or Enum, found type `{type(x)}`")
