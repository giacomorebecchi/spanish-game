import os
from io import StringIO
from typing import List, Optional

import pandas as pd

FOLDER = os.path.realpath(os.path.join(os.path.dirname(__file__), "txt"))


def find_files():
    return [
        os.path.join(FOLDER, el) for el in os.listdir(FOLDER) if el.endswith(".txt")
    ]


def remove_newlines(s):
    new_s = ""
    for i, char in enumerate(s):
        if (
            char == "\n"
            and i + 1 != len(s)
            and s[i + 1] == s[i + 1].lower()
            and s[i + 1].isalnum()
        ):
            new_s += " "
        else:
            new_s += char
    return new_s


def remove_brackets(s):
    new_s = ""
    skipc = 0
    for i, char in enumerate(s):
        if char == " " and i + 1 != len(s) and s[i + 1] == "(":
            skipc += 1
        elif char == ")" and skipc > 0:
            skipc -= 1
        elif skipc == 0:
            new_s += char
    return new_s


def main(letters: Optional[List] = None) -> None:
    if not letters:
        letters = find_files()
    else:
        letters = [os.path.join(FOLDER, letter + ".txt") for letter in letters]
    for file_name in letters:
        with open(file_name, mode="r") as f:
            s = f.read()
        s = s.replace("-\n", "").replace(",", ";").replace(": ", ",")
        s = remove_newlines(s)
        s = remove_brackets(s)
        try:
            df = pd.read_csv(StringIO(s.lower()), header=None).rename(
                columns={0: "Spanish", 1: "Italian"}
            )
            df.to_excel(
                file_name.removesuffix(".txt") + ".xlsx",
                index=False,
                columns=["Italian", "Spanish"],
            )
        except Exception as e:
            print(f"Failed for file {file_name}")
            print(e)
        # with open(
        #     os.path.join(FOLDER, file_name.removesuffix(".txt") + ".csv"), mode="wb"
        # ) as new_f:
        #     new_f.write(s.lower().encode())


if __name__ == "__main__":
    main()
    # main(["a"])
