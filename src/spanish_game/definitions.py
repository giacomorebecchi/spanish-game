import os

ROOT_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
)
DATA_DIR = os.path.join(ROOT_DIR, "data")
SPANISH_FILE = os.path.join(DATA_DIR, "Diccionario.xlsx")
