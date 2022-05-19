import os

from spanish_game.definitions import DATA_DIR, ROOT_DIR


def test_root_dir():
    assert os.path.isdir(ROOT_DIR)


def test_data_dir():
    assert os.path.isdir(DATA_DIR)
