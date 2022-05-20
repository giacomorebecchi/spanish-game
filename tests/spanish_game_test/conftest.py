from io import BytesIO
from typing import Callable, Dict

import pandas as pd
from pytest import fixture


@fixture(scope="function")
def vocabulary() -> Callable:
    d = {
        "Spanish": {0: "A_es", 1: "B_es", 2: "C_es"},
        "Italian": {0: "A_it", 1: "B_it", 2: "C_es"},
    }

    def get_vocabulary(orient: str = "dict") -> Dict:
        if orient == "dict":
            return d
        elif orient == "index":
            index_d = {}
            for k1, s in d.items():
                for k2, v in s.items():
                    index_d.setdefault(k2, {})[k1] = v
            return index_d

    return get_vocabulary


@fixture(scope="function")
def vocabulary_dict(vocabulary: Callable) -> Dict[str, Dict[int, str]]:
    return vocabulary("dict")


@fixture(scope="function")
def vocabulary_invDict(vocabulary: Callable) -> Dict[int, Dict[str, str]]:
    return vocabulary("index")


@fixture(scope="function")
def vocabulary_xlsxIO(vocabulary_dict: Dict[str, Dict[int, str]]) -> BytesIO:
    df = pd.DataFrame(vocabulary_dict)
    # Create your in memory BytesIO file.
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="openpyxl")
    df.to_excel(writer, sheet_name="Sheet1", index=False)
    writer.save()
    output.seek(0)  # Contains the Excel file in memory.
    return output
