from typing import Dict

import pandas as pd

from spanish_game.definitions import SPANISH_FILE


def load_vocabulary(
    file: str = SPANISH_FILE, orient: str = "dict"
) -> Dict[str, Dict[int, str]]:
    with open(file, mode="rb") as f:
        df: pd.DataFrame = pd.read_excel(f, sheet_name="Sheet1")
    return df.to_dict(orient=orient)
