from mltraq.utils.wordlist import words

n_words = len(words)


def uuid3words(uuid):
    """Convert UUID to a tripled "a.b.c" , where a b and c are words taken
    from a EN dictionary. It works like an hash function.

    Args:
        uuid (_type_): UUID to convert.

    Returns:
        _type_: string of the hashed UUID.
    """
    idx0 = (hash(uuid) + 0) % n_words
    idx1 = (hash(uuid) + 1) % n_words
    idx2 = (hash(uuid) + 2) % n_words
    return f"{words[idx0]}.{words[idx1]}.{words[idx2]}"
