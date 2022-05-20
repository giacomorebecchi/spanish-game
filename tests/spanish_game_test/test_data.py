from io import BytesIO
from typing import Callable
from unittest.mock import patch

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


@pytest.mark.parametrize("orient", ["dict", "index"])
def test_load_vocabulary(vocabulary_xlsxIO: BytesIO, vocabulary: Callable, orient: str):
    with patch("spanish_game.data.open") as open_mock:
        open_mock.return_value = vocabulary_xlsxIO
        voc = load_vocabulary("file/path/file.xslx", orient=orient)
        open_mock.assert_called_with("file/path/file.xslx", mode="rb")
    assert voc == vocabulary(orient)
