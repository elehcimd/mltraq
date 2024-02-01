from pprint import pprint

from mltraq.storage.serialization import NATIVE_DATABASE_TYPES
from mltraq.storage.serializers.datapak import BASIC_TYPES, COMPLEX_TYPES, CONTAINER_TYPES

print("NATIVE_DATABASE_TYPES")
pprint(NATIVE_DATABASE_TYPES, indent=2, width=70)
print("--\n")

print("BASIC_TYPES")
pprint(BASIC_TYPES, indent=2, width=70)
print("--\n")

print("CONTAINER_TYPES")
pprint(CONTAINER_TYPES, indent=2, width=70)
print("--\n")

print("COMPLEX_TYPES")
pprint(COMPLEX_TYPES, indent=2, width=70)
