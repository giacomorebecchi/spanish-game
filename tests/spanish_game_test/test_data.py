from io import BytesIO
from unittest.mock import patch

import pandas as pd
import pytest
from spanish_game.data import load_vocabulary, validate_vocabulary


def test_validate_vocabulary():
    vocabulary_langs = ["Spanish", "Italian"]
    languages = ["Italian", "Spanish"]
    assert validate_vocabulary(vocabulary_langs, languages)
    vocabulary_langs.append("Categories")
    assert validate_vocabulary(vocabulary_langs, languages)
    languages.append("English")
    with pytest.raises(Exception):
        assert validate_vocabulary(vocabulary_langs, languages)


def test_load_vocabulary(vocabulary_xlsxIO: BytesIO, vocabulary: pd.DataFrame):
    with patch("spanish_game.data.open") as open_mock:
        open_mock.return_value = vocabulary_xlsxIO
        df = load_vocabulary("file/path/file.xslx")
        open_mock.assert_called_with("file/path/file.xslx", mode="rb")
    assert (df == vocabulary).all(axis=None)
