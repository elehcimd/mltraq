import glob
import os

from spellchecker import SpellChecker, WordFrequency

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir + os.sep + os.pardir)
WHITELIST_PATHNAME = f"{PROJECT_DIR}/spellchecker.whitelist"


def init_spellchecker():
    """
    Initialize spellchecker with whitelist.
    """
    spell = SpellChecker()
    spell.word_frequency.load_text_file(WHITELIST_PATHNAME)
    return spell


def spellcheck_file(pathname, spell):
    """
    Spellcheck file `pathname` with `spell` spellchecker.
    """
    wf = WordFrequency()
    wf.load_text_file(pathname)
    tokens = wf.words()
    misspelled = spell.unknown(tokens)
    return misspelled


def test_spellchecker():
    """
    Test: spellcheck mkdocs files, honoring a whitelist.
    """
    pathnames = glob.glob(f"{PROJECT_DIR}/mkdocs/**/*.md", recursive=True)
    spell = init_spellchecker()
    misspelled = set()
    for pathname in pathnames:
        misspelled |= spellcheck_file(pathname, spell)

    if len(misspelled) > 0:
        # Report mispelled tokens, s.t. they can be either fixed or added to whitelist.
        print(f"=========== MISSSPLELLED ({len(misspelled)})")
        for word in misspelled:
            print(word)
        print("===========")

    assert len(misspelled) == 0
