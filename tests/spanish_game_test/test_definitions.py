import os
from pathlib import PurePosixPath

from spanish_game.definitions import DATA_DIR, ROOT_DIR, VOCABULARY_FILE


def test_root_dir():
    assert os.path.isdir(ROOT_DIR)


def test_data_dir():
    assert os.path.isdir(DATA_DIR)


def test_vocabulary_file():
    assert os.path.isfile(VOCABULARY_FILE)
    assert PurePosixPath(VOCABULARY_FILE).suffix == ".xlsx"
