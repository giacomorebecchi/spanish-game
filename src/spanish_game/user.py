import getpass
import os
from itertools import permutations, product
from typing import Dict, List

import bcrypt
import numpy as np
import pandas as pd

from .definitions import DATA_DIR, LANGUAGES
from .exceptions import ExistentUserError, OverwritingError, PasswordRetriesLimitError
from .game_mode import Mode
from .settings import get_settings
from .vocabulary import Vocabulary


class User:
    def __init__(self, username: str) -> None:
        self.settings = get_settings()
        self.username = username
        self.user_dir = self.get_user_dir()
        if self.user_exists():
            retries = 0
            if self.check_password():  # if no password was set
                pass
            else:  # if there is a password
                while True:
                    password = getpass.getpass(
                        f"Hello {self.username}! Type your password: "
                    ).encode()
                    if self.check_password(password):  # if password is correct
                        pass
                    else:  # if password is wrong
                        retries += 1
                        if (
                            remaining_retries := self.settings.MAX_RETRIES_PASSWORD
                            - retries
                        ) == 0:  # if retries limit reached
                            print("You reached the maximum number of retries.")
                            raise PasswordRetriesLimitError
                        else:  # if there are tentatives remaining
                            print(
                                f"Wrong password, please try again. {remaining_retries} tentatives remaining."
                            )
        else:
            self.create_new_user()
        self.data = self.UserData(self.get_data_fp())

    def get_user_dir(self) -> str:
        return os.path.join(DATA_DIR, "users", self.username)

    def user_exists(self) -> bool:
        return os.path.isdir(self.user_dir) and os.listdir(self.user_dir)

    def create_user_dir(self) -> None:
        if os.path.isdir(self.user_dir):
            if os.listdir(self.user_dir):
                raise ExistentUserError
            else:
                return None  # do nothing
        else:
            os.mkdir(self.user_dir)

    def create_new_user(self) -> None:
        self.create_user_dir()
        print(f"Welcome, {self.username}!")
        while True:
            password = getpass.getpass("Choose a password: ")
            if password == getpass.getpass("Confirm the password: "):
                self.store_password(password.encode())
                print("Password created!")
                break
            else:
                print("The passwords do not correspond. Please retry!")
                continue

    def store_password(self, password: bytes) -> None:
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(12))
        password_fp = self.get_password_fp()
        with open(password_fp, mode="wb") as f:
            f.write(hashed_password)

    def read_hashed_password(self) -> bytes:
        password_file = self.get_password_fp()
        with open(password_file, mode="rb") as f:
            password = f.read()
        return password

    def get_password_fp(self) -> str:
        return os.path.join(self.get_user_dir(), "pwd.txt")

    def check_password(self, password: bytes = b"") -> bool:
        hashed_password = self.read_hashed_password()
        return bcrypt.checkpw(password, hashed_password)

    def get_data_fp(self) -> str:
        return os.path.join(self.get_user_dir(), "data.parquet")

    def write_user_data(self) -> None:
        data_fp = self.get_data_fp()
        self.data.data.to_parquet(data_fp)

    class UserData:
        modes: List[Mode] = [
            Mode(name="all", message="All words", inclusive=False),
            Mode(name="new", message="New words", inclusive=False),
            Mode(
                name="last-1-error",
                message="Words you got wrong the last time you saw them",
                inclusive=True,
            ),
            Mode(
                name="last-n-error",
                message=f"Words you got wrong the last {5} times you saw them",
                inclusive=True,
            ),  # TODO: parametrize
            Mode(
                name="low-score",
                message="Words that are usually difficult for you",
                inclusive=True,
            ),
        ]

        def __init__(self, data_fp: str) -> None:
            self.columns = self._get_columns()
            if os.path.isfile(data_fp):
                self.data = pd.read_parquet(data_fp, columns=self.columns)
            else:
                self.data = pd.DataFrame(columns=self.columns)
                self.data.index.name = "id"

        def _get_columns(self) -> List[str]:
            columns = [
                *LANGUAGES,
            ]
            columns_per_combination = [
                "n-rounds",
                "tot-score",
                *{"score-" + str(i + 1) for i in range(5)},  # TODO: parametrize
            ]
            languages_combination = [
                l1 + "-" + l2 for l1, l2 in permutations(LANGUAGES, 2)
            ]
            columns.extend(
                [
                    langs + "_" + attr
                    for langs, attr in product(
                        languages_combination, columns_per_combination
                    )
                ]
            )
            return columns

        def ids_consistent(self, vocabulary: Vocabulary) -> bool:
            return True  # TODO

        def get_modes_indices(self, input_lang: str, output_lang: str) -> List[Mode]:
            correct_modes = []
            for mode in self.modes:
                mode._get_indices(self.data, input_lang, output_lang)
                if mode.ids or not (mode.inclusive):
                    correct_modes.append(mode)
            return correct_modes

        def update_game_result(
            self, input_lang: str, output_lang: str, result: List[Dict]
        ) -> None:
            def get_col(suffix: str, n: int = None):
                is_n = 1 if n is not None else 0
                return f"{input_lang}-{output_lang}_{suffix}" + is_n * ("-" + str(n))

            def safe_add(a: float, b: float) -> float:
                return b if np.isnan(a) else a + b

            for round in result:
                if (id := round["id"]) in self.data.index:
                    self.data.loc[id, get_col("n-rounds")] = safe_add(
                        self.data.loc[id, get_col("n-rounds")], 1
                    )
                    self.data.loc[id, get_col("tot-score")] = safe_add(
                        self.data.loc[id, get_col("tot-score")], round["score"]
                    )
                    for i in range(5, 1, -1):
                        self.data.loc[id, get_col("score", i)] = self.data.loc[
                            id, get_col("score", i - 1)
                        ]
                    self.data.loc[id, get_col("score", 1)] = round["score"]
                else:
                    self.data.loc[id, input_lang] = round[input_lang]
                    self.data.loc[id, output_lang] = round[output_lang]
                    self.data.loc[id, get_col("n-rounds")] = 1
                    self.data.loc[id, get_col("tot-score")] = round["score"]
                    self.data.loc[id, get_col("score", 1)] = round["score"]


class AnonUser:
    pass  # TODO: Mock real User
