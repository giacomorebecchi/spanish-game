from io import BytesIO

import pandas as pd
from pytest import fixture


@fixture(scope="function")
def vocabulary() -> pd.DataFrame:
    d = {
        "Spanish": {0: "A_es", 1: "B_es", 2: "C_es"},
        "Italian": {0: "A_it", 1: "B_it", 2: "C_es"},
    }

    df = pd.DataFrame(d)
    return df


@fixture(scope="function")
def vocabulary_xlsxIO(vocabulary: pd.DataFrame) -> BytesIO:
    # Create your in memory BytesIO file.
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="openpyxl")
    vocabulary.to_excel(writer, sheet_name="Sheet1", index=False)
    writer.save()
    output.seek(0)  # Contains the Excel file in memory.
    return output
