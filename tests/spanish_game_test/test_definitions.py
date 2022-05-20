import os
from pathlib import PurePosixPath

from spanish_game.definitions import DATA_DIR, ROOT_DIR, SPANISH_FILE


def test_root_dir():
    assert os.path.isdir(ROOT_DIR)


def test_data_dir():
    assert os.path.isdir(DATA_DIR)


def test_spanish_file():
    assert os.path.isfile(SPANISH_FILE)
    assert PurePosixPath(SPANISH_FILE).suffix == ".xlsx"
