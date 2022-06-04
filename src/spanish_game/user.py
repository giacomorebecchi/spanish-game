import os

import bcrypt

from spanish_game.definitions import DATA_DIR
from spanish_game.exceptions import ExistentUserError
from spanish_game.settings import get_settings


class User:
    def __init__(self, username: str) -> None:
        self.settings = get_settings()
        self.username = username
        self.user_dir = self.get_user_dir()
        if self.user_exists():
            retries = 0
            while True:
                self.password = input(
                    f"Hello {self.username}! Type your password: "
                ).encode()
                if self.check_password():
                    break
                else:
                    retries += 1
                    if (
                        remaining_retries := self.settings.MAX_RETRIES_PASSWORD
                        - retries
                    ) == 0:
                        print("You reached the maximum number of retries. Good bye!")
                        break
                    else:
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
            confirm_password = input("Confirm the password: ")
            if password == confirm_password:
                self.password = password.encode()
                self.store_password()
                print("Password created!")
                break
            else:
                print("The passwords do not correspond. Please retry!")
                continue

    def store_password(self) -> None:
        hashed_password = bcrypt.hashpw(self.password, bcrypt.gensalt(12))
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

    def check_password(self) -> bool:
        hashed_password = self.read_hashed_password()
        return bcrypt.checkpw(self.password, hashed_password)
