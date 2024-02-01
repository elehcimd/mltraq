"""
Dictionary generated and manually reviewed to mark opcodes as safe/unsafe.

We disallow all things class/reduce-related, allowing only the stack/memo management ops,
lists, dicts, tuples, sets, ints, floats, strings and bytes.
(eg, opcodes for buffers introduced in pickle5 are not allowed, as they're not useful
to encode the types listed above.)

# You can review the pickletools's implementation source code at:
# https://github.com/python/cpython/blob/main/Lib/pickletools.py

# Code to regenerate the dictionary:

--
from textwrap import indent
from pickletools opcodes

safe_opcodes = print("{")
for opcode in opcodes:
    comment = indent(f'opcode.code: {opcode.code} pcode.proto: {opcode.proto}\nopcode.doc:\n{opcode.doc}', '# ')
    print(f'"{opcode.name}" : False,\n{comment}\n')
print("}")
--

"""

pickle_safe_opcodes = {
    "INT": True,
    # opcode.code: I pcode.proto: 0
    # opcode.doc:
    # Push an integer or bool.
    #       The argument is a newline-terminated decimal literal string.
    #       The intent may have been that this always fit in a short Python int,
    #       but INT can be generated in pickles written on a 64-bit box that
    #       require a Python long on a 32-bit box.  The difference between this
    #       and LONG then is that INT skips a trailing 'L', and produces a short
    #       int whenever possible.
    #       Another difference is due to that, when bool was introduced as a
    #       distinct type in 2.3, builtin names True and False were also added to
    #       2.2.2, mapping to ints 1 and 0.  For compatibility in both directions,
    #       True gets pickled as INT + "I01\n", and False as INT + "I00\n".
    #       Leading zeroes are never produced for a genuine integer.  The 2.3
    #       (and later) unpicklers special-case these and return bool instead;
    #       earlier unpicklers ignore the leading "0" and return the int.
    "BININT": True,
    # opcode.code: J pcode.proto: 1
    # opcode.doc:
    # Push a four-byte signed integer.
    #       This handles the full range of Python (short) integers on a 32-bit
    #       box, directly as binary bytes (1 for the opcode and 4 for the integer).
    #       If the integer is non-negative and fits in 1 or 2 bytes, pickling via
    #       BININT1 or BININT2 saves space.
    "BININT1": True,
    # opcode.code: K pcode.proto: 1
    # opcode.doc:
    # Push a one-byte unsigned integer.
    #       This is a space optimization for pickling very small non-negative ints,
    #       in range(256).
    "BININT2": True,
    # opcode.code: M pcode.proto: 1
    # opcode.doc:
    # Push a two-byte unsigned integer.
    #       This is a space optimization for pickling small positive ints, in
    #       range(256, 2**16).  Integers in range(256) can also be pickled via
    #       BININT2, but BININT1 instead saves a byte.
    "LONG": True,
    # opcode.code: L pcode.proto: 0
    # opcode.doc:
    # Push a long integer.
    #       The same as INT, except that the literal ends with 'L', and always
    #       unpickles to a Python long.  There doesn't seem a real purpose to the
    #       trailing 'L'.
    #       Note that LONG takes time quadratic in the number of digits when
    #       unpickling (this is simply due to the nature of decimal->binary
    #       conversion).  Proto 2 added linear-time (in C; still quadratic-time
    #       in Python) LONG1 and LONG4 opcodes.
    "LONG1": True,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Long integer using one-byte length.
    #       A more efficient encoding of a Python long; the long1 encoding
    #       says it all.
    "LONG4": False,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Long integer using found-byte length.
    #       A more efficient encoding of a Python long; the long4 encoding
    #       says it all.
    "STRING": True,
    # opcode.code: S pcode.proto: 0
    # opcode.doc:
    # Push a Python string object.
    #       The argument is a repr-style string, with bracketing quote characters,
    #       and perhaps embedded escapes.  The argument extends until the next
    #       newline character.  These are usually decoded into a str instance
    #       using the encoding given to the Unpickler constructor. or the default,
    #       'ASCII'.  If the encoding given was 'bytes' however, they will be
    #       decoded as bytes object instead.
    "BINSTRING": True,
    # opcode.code: T pcode.proto: 1
    # opcode.doc:
    # Push a Python string object.
    #       There are two arguments: the first is a 4-byte little-endian
    #       signed int giving the number of bytes in the string, and the
    #       second is that many bytes, which are taken literally as the string
    #       content.  These are usually decoded into a str instance using the
    #       encoding given to the Unpickler constructor. or the default,
    #       'ASCII'.  If the encoding given was 'bytes' however, they will be
    #       decoded as bytes object instead.
    "SHORT_BINSTRING": True,
    # opcode.code: U pcode.proto: 1
    # opcode.doc:
    # Push a Python string object.
    #       There are two arguments: the first is a 1-byte unsigned int giving
    #       the number of bytes in the string, and the second is that many
    #       bytes, which are taken literally as the string content.  These are
    #       usually decoded into a str instance using the encoding given to
    #       the Unpickler constructor. or the default, 'ASCII'.  If the
    #       encoding given was 'bytes' however, they will be decoded as bytes
    #       object instead.
    "BINBYTES": True,
    # opcode.code: B pcode.proto: 3
    # opcode.doc:
    # Push a Python bytes object.
    #       There are two arguments:  the first is a 4-byte little-endian unsigned int
    #       giving the number of bytes, and the second is that many bytes, which are
    #       taken literally as the bytes content.
    "SHORT_BINBYTES": True,
    # opcode.code: C pcode.proto: 3
    # opcode.doc:
    # Push a Python bytes object.
    #       There are two arguments:  the first is a 1-byte unsigned int giving
    #       the number of bytes, and the second is that many bytes, which are taken
    #       literally as the string content.
    "BINBYTES8": True,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Push a Python bytes object.
    #       There are two arguments:  the first is an 8-byte unsigned int giving
    #       the number of bytes in the string, and the second is that many bytes,
    #       which are taken literally as the string content.
    "BYTEARRAY8": True,
    # opcode.code:  pcode.proto: 5
    # opcode.doc:
    # Push a Python bytearray object.
    #       There are two arguments:  the first is an 8-byte unsigned int giving
    #       the number of bytes in the bytearray, and the second is that many bytes,
    #       which are taken literally as the bytearray content.
    "NEXT_BUFFER": False,
    # opcode.code:  pcode.proto: 5
    # opcode.doc:
    # Push an out-of-band buffer object.
    "READONLY_BUFFER": False,
    # opcode.code:  pcode.proto: 5
    # opcode.doc:
    # Make an out-of-band buffer object read-only.
    "NONE": True,
    # opcode.code: N pcode.proto: 0
    # opcode.doc:
    # Push None on the stack.
    "NEWTRUE": True,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Push True onto the stack.
    "NEWFALSE": True,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Push False onto the stack.
    "UNICODE": True,
    # opcode.code: V pcode.proto: 0
    # opcode.doc:
    # Push a Python Unicode string object.
    #       The argument is a raw-unicode-escape encoding of a Unicode string,
    #       and so may contain embedded escape sequences.  The argument extends
    #       until the next newline character.
    "SHORT_BINUNICODE": True,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Push a Python Unicode string object.
    #       There are two arguments:  the first is a 1-byte little-endian signed int
    #       giving the number of bytes in the string.  The second is that many
    #       bytes, and is the UTF-8 encoding of the Unicode string.
    "BINUNICODE": True,
    # opcode.code: X pcode.proto: 1
    # opcode.doc:
    # Push a Python Unicode string object.
    #       There are two arguments:  the first is a 4-byte little-endian unsigned int
    #       giving the number of bytes in the string.  The second is that many
    #       bytes, and is the UTF-8 encoding of the Unicode string.
    "BINUNICODE8": True,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Push a Python Unicode string object.
    #       There are two arguments:  the first is an 8-byte little-endian signed int
    #       giving the number of bytes in the string.  The second is that many
    #       bytes, and is the UTF-8 encoding of the Unicode string.
    "FLOAT": True,
    # opcode.code: F pcode.proto: 0
    # opcode.doc:
    # Newline-terminated decimal float literal.
    #       The argument is repr(a_float), and in general requires 17 significant
    #       digits for roundtrip conversion to be an identity (this is so for
    #       IEEE-754 double precision values, which is what Python float maps to
    #       on most boxes).
    #       In general, FLOAT cannot be used to transport infinities, NaNs, or
    #       minus zero across boxes (or even on a single box, if the platform C
    #       library can't read the strings it produces for such things -- Windows
    #       is like that), but may do less damage than BINFLOAT on boxes with
    #       greater precision or dynamic range than IEEE-754 double.
    "BINFLOAT": True,
    # opcode.code: G pcode.proto: 1
    # opcode.doc:
    # Float stored in binary form, with 8 bytes of data.
    #       This generally requires less than half the space of FLOAT encoding.
    #       In general, BINFLOAT cannot be used to transport infinities, NaNs, or
    #       minus zero, raises an exception if the exponent exceeds the range of
    #       an IEEE-754 double, and retains no more than 53 bits of precision (if
    #       there are more than that, "add a half and chop" rounding is used to
    #       cut it back to 53 significant bits).
    "EMPTY_LIST": True,
    # opcode.code: ] pcode.proto: 1
    # opcode.doc:
    # Push an empty list.
    "APPEND": True,
    # opcode.code: a pcode.proto: 0
    # opcode.doc:
    # Append an object to a list.
    #       Stack before:  ... pylist anyobject
    #       Stack after:   ... pylist+[anyobject]
    #       although pylist is really extended in-place.
    "APPENDS": True,
    # opcode.code: e pcode.proto: 1
    # opcode.doc:
    # Extend a list by a slice of stack objects.
    #       Stack before:  ... pylist markobject stackslice
    #       Stack after:   ... pylist+stackslice
    #       although pylist is really extended in-place.
    "LIST": True,
    # opcode.code: l pcode.proto: 0
    # opcode.doc:
    # Build a list out of the topmost stack slice, after markobject.
    #       All the stack entries following the topmost markobject are placed into
    #       a single Python list, which single list object replaces all of the
    #       stack from the topmost markobject onward.  For example,
    #       Stack before: ... markobject 1 2 3 'abc'
    #       Stack after:  ... [1, 2, 3, 'abc']
    "EMPTY_TUPLE": True,
    # opcode.code: ) pcode.proto: 1
    # opcode.doc:
    # Push an empty tuple.
    "TUPLE": True,
    # opcode.code: t pcode.proto: 0
    # opcode.doc:
    # Build a tuple out of the topmost stack slice, after markobject.
    #       All the stack entries following the topmost markobject are placed into
    #       a single Python tuple, which single tuple object replaces all of the
    #       stack from the topmost markobject onward.  For example,
    #       Stack before: ... markobject 1 2 3 'abc'
    #       Stack after:  ... (1, 2, 3, 'abc')
    "TUPLE1": True,
    # opcode.code: #  pcode.proto: 2
    # opcode.doc:
    # Build a one-tuple out of the topmost item on the stack.
    #       This code pops one value off the stack and pushes a tuple of
    #       length 1 whose one item is that value back onto it.
    "TUPLE2": True,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Build a two-tuple out of the top two items on the stack.
    #       This code pops two values off the stack and pushes a tuple of
    #       length 2 whose items are those values back onto it.
    "TUPLE3": True,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Build a three-tuple out of the top three items on the stack.
    #       This code pops three values off the stack and pushes a tuple of
    #       length 3 whose items are those values back onto it.
    "EMPTY_DICT": True,
    # opcode.code: } pcode.proto: 1
    # opcode.doc:
    # Push an empty dict.
    "DICT": True,
    # opcode.code: d pcode.proto: 0
    # opcode.doc:
    # Build a dict out of the topmost stack slice, after markobject.
    #       All the stack entries following the topmost markobject are placed into
    #       a single Python dict, which single dict object replaces all of the
    #       stack from the topmost markobject onward.  The stack slice alternates
    #       key, value, key, value, ....  For example,
    #       Stack before: ... markobject 1 2 3 'abc'
    #       Stack after:  ... {1: 2, 3: 'abc'}
    "SETITEM": True,
    # opcode.code: s pcode.proto: 0
    # opcode.doc:
    # Add a key+value pair to an existing dict.
    #       Stack before:  ... pydict key value
    #       Stack after:   ... pydict
    #       where pydict has been modified via pydict[key] = value.
    "SETITEMS": True,
    # opcode.code: u pcode.proto: 1
    # opcode.doc:
    # Add an arbitrary number of key+value pairs to an existing dict.
    #       The slice of the stack following the topmost markobject is taken as
    #       an alternating sequence of keys and values, added to the dict
    #       immediately under the topmost markobject.  Everything at and after the
    #       topmost markobject is popped, leaving the mutated dict at the top
    #       of the stack.
    #       Stack before:  ... pydict markobject key_1 value_1 ... key_n value_n
    #       Stack after:   ... pydict
    #       where pydict has been modified via pydict[key_i] = value_i for i in
    #       1, 2, ..., n, and in that order.
    "EMPTY_SET": True,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Push an empty set.
    "ADDITEMS": True,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Add an arbitrary number of items to an existing set.
    #       The slice of the stack following the topmost markobject is taken as
    #       a sequence of items, added to the set immediately under the topmost
    #       markobject.  Everything at and after the topmost markobject is popped,
    #       leaving the mutated set at the top of the stack.
    #       Stack before:  ... pyset markobject item_1 ... item_n
    #       Stack after:   ... pyset
    #       where pyset has been modified via pyset.add(item_i) = item_i for i in
    #       1, 2, ..., n, and in that order.
    "FROZENSET": True,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Build a frozenset out of the topmost slice, after markobject.
    #       All the stack entries following the topmost markobject are placed into
    #       a single Python frozenset, which single frozenset object replaces all
    #       of the stack from the topmost markobject onward.  For example,
    #       Stack before: ... markobject 1 2 3
    #       Stack after:  ... frozenset({1, 2, 3})
    "POP": True,
    # opcode.code: 0 pcode.proto: 0
    # opcode.doc:
    # Discard the top stack item, shrinking the stack by one item.
    "DUP": True,
    # opcode.code: 2 pcode.proto: 0
    # opcode.doc:
    # Push the top stack item onto the stack again, duplicating it.
    "MARK": True,
    # opcode.code: ( pcode.proto: 0
    # opcode.doc:
    # Push markobject onto the stack.
    #       markobject is a unique object, used by other opcodes to identify a
    #       region of the stack containing a variable number of objects for them
    #       to work on.  See markobject.doc for more detail.
    "POP_MARK": True,
    # opcode.code: 1 pcode.proto: 1
    # opcode.doc:
    # Pop all the stack objects at and above the topmost markobject.
    #       When an opcode using a variable number of stack objects is done,
    #       POP_MARK is used to remove those objects, and to remove the markobject
    #       that delimited their starting position on the stack.
    "GET": True,
    # opcode.code: g pcode.proto: 0
    # opcode.doc:
    # Read an object from the memo and push it on the stack.
    #       The index of the memo object to push is given by the newline-terminated
    #       decimal string following.  BINGET and LONG_BINGET are space-optimized
    #       versions.
    "BINGET": True,
    # opcode.code: h pcode.proto: 1
    # opcode.doc:
    # Read an object from the memo and push it on the stack.
    #       The index of the memo object to push is given by the 1-byte unsigned
    #       integer following.
    "LONG_BINGET": True,
    # opcode.code: j pcode.proto: 1
    # opcode.doc:
    # Read an object from the memo and push it on the stack.
    #       The index of the memo object to push is given by the 4-byte unsigned
    #       little-endian integer following.
    "PUT": True,
    # opcode.code: p pcode.proto: 0
    # opcode.doc:
    # Store the stack top into the memo.  The stack is not popped.
    #       The index of the memo location to write into is given by the newline-
    #       terminated decimal string following.  BINPUT and LONG_BINPUT are
    #       space-optimized versions.
    "BINPUT": False,
    # opcode.code: q pcode.proto: 1
    # opcode.doc:
    # Store the stack top into the memo.  The stack is not popped.
    #       The index of the memo location to write into is given by the 1-byte
    #       unsigned integer following.
    "LONG_BINPUT": True,
    # opcode.code: r pcode.proto: 1
    # opcode.doc:
    # Store the stack top into the memo.  The stack is not popped.
    #       The index of the memo location to write into is given by the 4-byte
    #       unsigned little-endian integer following.
    "MEMOIZE": True,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Store the stack top into the memo.  The stack is not popped.
    #       The index of the memo location to write is the number of
    #       elements currently present in the memo.
    "EXT1": False,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Extension code.
    #       This code and the similar EXT2 and EXT4 allow using a registry
    #       of popular objects that are pickled by name, typically classes.
    #       It is envisioned that through a global negotiation and
    #       registration process, third parties can set up a mapping between
    #       ints and object names.
    #       In order to guarantee pickle interchangeability, the extension
    #       code registry ought to be global, although a range of codes may
    #       be reserved for private use.
    #       EXT1 has a 1-byte integer argument.  This is used to index into the
    #       extension registry, and the object at that index is pushed on the stack.
    "EXT2": False,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Extension code.
    #       See EXT1.  EXT2 has a two-byte integer argument.
    "EXT4": False,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Extension code.
    #       See EXT1.  EXT4 has a four-byte integer argument.
    "GLOBAL": False,
    # opcode.code: c pcode.proto: 0
    # opcode.doc:
    # Push a global object (module.attr) on the stack.
    #       Two newline-terminated strings follow the GLOBAL opcode.  The first is
    #       taken as a module name, and the second as a class name.  The class
    #       object module.class is pushed on the stack.  More accurately, the
    #       object returned by self.find_class(module, class) is pushed on the
    #       stack, so unpickling subclasses can override this form of lookup.
    "STACK_GLOBAL": False,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Push a global object (module.attr) on the stack.
    "REDUCE": False,
    # opcode.code: R pcode.proto: 0
    # opcode.doc:
    # Push an object built from a callable and an argument tuple.
    #       The opcode is named to remind of the __reduce__() method.
    #       Stack before: ... callable pytuple
    #       Stack after:  ... callable(*pytuple)
    #       The callable and the argument tuple are the first two items returned
    #       by a __reduce__ method.  Applying the callable to the argtuple is
    #       supposed to reproduce the original object, or at least get it started.
    #       If the __reduce__ method returns a 3-tuple, the last component is an
    #       argument to be passed to the object's __setstate__, and then the REDUCE
    #       opcode is followed by code to create setstate's argument, and then a
    #       BUILD opcode to apply  __setstate__ to that argument.
    #       If not isinstance(callable, type), REDUCE complains unless the
    #       callable has been registered with the copyreg module's
    #       safe_constructors dict, or the callable has a magic
    #       '__safe_for_unpickling__' attribute with a true value.  I'm not sure
    #       why it does this, but I've sure seen this complaint often enough when
    #       I didn't want to <wink>.
    "BUILD": False,
    # opcode.code: b pcode.proto: 0
    # opcode.doc:
    # Finish building an object, via __setstate__ or dict update.
    "INST": False,
    # opcode.code: i pcode.proto: 0
    # opcode.doc:
    # Build a class instance.
    #       This is the protocol 0 version of protocol 1's OBJ opcode.
    #       INST is followed by two newline-terminated strings, giving a
    #       module and class name, just as for the GLOBAL opcode (and see
    #       GLOBAL for more details about that).  self.find_class(module, name)
    #       is used to get a class object.
    #       In addition, all the objects on the stack following the topmost
    #       markobject are gathered into a tuple and popped (along with the
    #       topmost markobject), just as for the TUPLE opcode.
    #       Now it gets complicated.  If all of these are true:
    #         + The argtuple is empty (markobject was at the top of the stack
    #           at the start).
    #         + The class object does not have a __getinitargs__ attribute.
    #       then we want to create an old-style class instance without invoking
    #       its __init__() method (pickle has waffled on this over the years; not
    #       calling __init__() is current wisdom).  In this case, an instance of
    #       an old-style dummy class is created, and then we try to rebind its
    #       __class__ attribute to the desired class object.  If this succeeds,
    #       the new instance object is pushed on the stack, and we're done.
    #       Else (the argtuple is not empty, it's not an old-style class object,
    #       or the class object does have a __getinitargs__ attribute), the code
    #       first insists that the class object have a __safe_for_unpickling__
    #       attribute.  Unlike as for the __safe_for_unpickling__ check in REDUCE,
    #       it doesn't matter whether this attribute has a true or false value, it
    #       only matters whether it exists (this is a bug).  If
    #       __safe_for_unpickling__ doesn't exist, UnpicklingError is raised.
    #       Else (the class object does have a __safe_for_unpickling__ attr),
    #       the class object obtained from INST's arguments is applied to the
    #       argtuple obtained from the stack, and the resulting instance object
    #       is pushed on the stack.
    #       NOTE:  checks for __safe_for_unpickling__ went away in Python 2.3.
    #       NOTE:  the distinction between old-style and new-style classes does
    #              not make sense in Python 3.
    "OBJ": False,
    # opcode.code: o pcode.proto: 1
    # opcode.doc:
    # Build a class instance.
    #       This is the protocol 1 version of protocol 0's INST opcode, and is
    #       very much like it.  The major difference is that the class object
    #       is taken off the stack, allowing it to be retrieved from the memo
    #       repeatedly if several instances of the same class are created.  This
    #       can be much more efficient (in both time and space) than repeatedly
    #       embedding the module and class names in INST opcodes.
    #       Unlike INST, OBJ takes no arguments from the opcode stream.  Instead
    #       the class object is taken off the stack, immediately above the
    #       topmost markobject:
    #       Stack before: ... markobject classobject stackslice
    #       Stack after:  ... new_instance_object
    #       As for INST, the remainder of the stack above the markobject is
    #       gathered into an argument tuple, and then the logic seems identical,
    #       except that no __safe_for_unpickling__ check is done (this is
    #       a bug).  See INST for the gory details.
    #       NOTE:  In Python 2.3, INST and OBJ are identical except for how they
    #       get the class object.  That was always the intent; the implementations
    #       had diverged for accidental reasons.
    "NEWOBJ": False,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Build an object instance.
    #       The stack before should be thought of as containing a class
    #       object followed by an argument tuple (the tuple being the stack
    #       top).  Call these cls and args.  They are popped off the stack,
    #       and the value returned by cls.__new__(cls, *args) is pushed back
    #       onto the stack.
    "NEWOBJ_EX": False,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Build an object instance.
    #       The stack before should be thought of as containing a class
    #       object followed by an argument tuple and by a keyword argument dict
    #       (the dict being the stack top).  Call these cls and args.  They are
    #       popped off the stack, and the value returned by
    #       cls.__new__(cls, *args, *kwargs) is  pushed back  onto the stack.
    "PROTO": True,
    # opcode.code:  pcode.proto: 2
    # opcode.doc:
    # Protocol version indicator.
    #       For protocol 2 and above, a pickle must start with this opcode.
    #       The argument is the protocol version, an int in range(2, 256).
    "STOP": True,
    # opcode.code: . pcode.proto: 0
    # opcode.doc:
    # Stop the unpickling machine.
    #       Every pickle ends with this opcode.  The object at the top of the stack
    #       is popped, and that's the result of unpickling.  The stack should be
    #       empty then.
    "FRAME": True,
    # opcode.code:  pcode.proto: 4
    # opcode.doc:
    # Indicate the beginning of a new frame.
    #       The unpickler may use this opcode to safely prefetch data from its
    #       underlying stream.
    "PERSID": False,
    # opcode.code: P pcode.proto: 0
    # opcode.doc:
    # Push an object identified by a persistent ID.
    #       The pickle module doesn't define what a persistent ID means.  PERSID's
    #       argument is a newline-terminated str-style (no embedded escapes, no
    #       bracketing quote characters) string, which *is* "the persistent ID".
    #       The unpickler passes this string to self.persistent_load().  Whatever
    #       object that returns is pushed on the stack.  There is no implementation
    #       of persistent_load() in Python's unpickler:  it must be supplied by an
    #       unpickler subclass.
    "BINPERSID": False,
    # opcode.code: Q pcode.proto: 1
    # opcode.doc:
    # Push an object identified by a persistent ID.
    #       Like PERSID, except the persistent ID is popped off the stack (instead
    #       of being a string embedded in the opcode bytestream).  The persistent
    #       ID is passed to self.persistent_load(), and whatever object that
    #       returns is pushed on the stack.  See PERSID for more detail.
}

# Set of safe opcodes to use.
pickle_safe_opcodes_set = {opcode for opcode in pickle_safe_opcodes.keys() if pickle_safe_opcodes[opcode]}
