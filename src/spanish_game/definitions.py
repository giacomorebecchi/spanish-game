import os
from typing import List

ROOT_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
)
DATA_DIR = os.path.join(ROOT_DIR, "data")
VOCABULARY_FILE = os.path.join(DATA_DIR, "vocabulary.xlsx")

LANGUAGES = ["Italian", "Spanish"]

_accent_equivalents = [
    {"a", "á", "à"},
    {"n", "ñ"},
    {"e", "é", "è"},
    {"i", "í", "ì"},
    {"o", "ó", "ò"},
    {"u", "ù", "ú"},
]


def _get_accent_equivalents(map_: List):
    d = {char: {x for x in l if x != char} for l in map_ for char in l}
    return d


ACCENT_EQUIVALENTS = _get_accent_equivalents(_accent_equivalents)
