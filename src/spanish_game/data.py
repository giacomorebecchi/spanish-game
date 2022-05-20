from typing import Dict, List

import pandas as pd

from spanish_game.definitions import LANGUAGES, VOCABULARY_FILE


def validate_vocabulary(
    vocabulary_langs: List[str], definition_langs: List[str] = LANGUAGES
) -> None:
    diff = set.difference(set(definition_langs), set(vocabulary_langs))
    if diff:
        raise Exception("Vocabulary file does not contain languages {diff}.")
    return True


def load_vocabulary(
    file: str = VOCABULARY_FILE, orient: str = "dict"
) -> Dict[str, Dict[int, str]]:
    with open(file, mode="rb") as f:
        df: pd.DataFrame = pd.read_excel(f, sheet_name="Sheet1")
    validate_vocabulary(df.columns)
    return df.to_dict(orient=orient)
