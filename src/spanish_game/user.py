import getpass
import os

import bcrypt
import pandas as pd

from spanish_game.definitions import DATA_DIR
from spanish_game.exceptions import (
    ExistentUserError,
    OverwritingError,
    PasswordRetriesLimitError,
)
from spanish_game.settings import get_settings


class User:
    def __init__(self, username: str) -> None:
        self.settings = get_settings()
        self.username = username
        self.user_dir = self.get_user_dir()
        if self.user_exists():
            retries = 0
            if self.check_password():  # if no password was set
                return None
            else:  # if there is a password
                while True:
                    password = getpass.getpass(
                        f"Hello {self.username}! Type your password: "
                    ).encode()
                    if self.check_password(password):  # if password is correct
                        return None
                    else:  # if password is wrong
                        retries += 1
                        if (
                            remaining_retries := self.settings.MAX_RETRIES_PASSWORD
                            - retries
                        ) == 0:  # if retries limit reached
                            print(
                                "You reached the maximum number of retries. Good bye!"
                            )
                            raise PasswordRetriesLimitError
                        else:  # if there are tentatives remaining
                            print(
                                f"Wrong password, please try again. {remaining_retries} tentatives remaining."
                            )
        else:
            self.create_new_user()

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
        print("New user created!")
        while True:
            password = input("Choose a password: ")
            if password == input("Confirm the password: "):
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

    def get_user_data(self, columns=None) -> pd.DataFrame:
        data_fp = self.get_data_fp()
        if os.path.isfile(data_fp):
            return pd.read_parquet(data_fp, columns=columns)
        else:
            return pd.DataFrame(columns=columns)

    def write_user_data(self, df: pd.DataFrame = None) -> None:
        data_fp = self.get_data_fp()
        if df is None:
            if os.path.isfile(data_fp):
                raise OverwritingError(
                    f"You are trying to overwrite an existing file with an empty one for user: {self.username}"
                )
            else:
                df = pd.DataFrame()
        df.to_parquet(data_fp)
