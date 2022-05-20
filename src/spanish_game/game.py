import random
import re
from typing import Callable, Dict

import inquirer
import numpy as np
from inquirer import errors

from spanish_game.data import load_vocabulary
from spanish_game.definitions import LANGUAGES


class Game:
    def __init__(self) -> None:
        self.vocabulary = load_vocabulary()
        self.available_langs = LANGUAGES
        inquiry = self._inquire()
        self.username = inquiry["username"]
        self.source_lang = inquiry["source_lang"]
        self.reply_lang = inquiry["reply_lang"]
        self.n_rounds = int(inquiry["n_rounds"])
        self.points = 0
        self.play_game()

    def inquire_validator(
        self, answers: Dict[str, str], current: str, validate: Callable, message: str
    ) -> bool:
        if validate(current):
            return True
        else:
            raise errors.ValidationError(current, message)

    def _inquire(self) -> Dict[str, str]:
        questions = [
            inquirer.Text(
                name="username",
                message="Input your username",
                default="anonUser",
                validate=lambda answers, current: self.inquire_validator(
                    answers,
                    current,
                    lambda x: re.match(re.compile(r"[a-zA-Z0-9]{4,12}"), x),
                    "Username must be only formed by letters or numbers, length of 4 to 12.",
                ),
            ),
            inquirer.List(
                name="source_lang",
                message="From which language would you like to translate?",
                choices=self.available_langs,
                carousel=True,
            ),
            inquirer.List(
                name="reply_lang",
                message="To which language would you like to translate?",
                choices=lambda answers: [
                    lang
                    for lang in self.available_langs
                    if lang not in answers.values()
                ],
                carousel=True,
            ),
            inquirer.Text(
                name="n_rounds",
                message="How many rounds would you like to play?",
                validate=lambda answers, current: self.inquire_validator(
                    answers,
                    current,
                    lambda x: re.match(re.compile(r"[0-9]+"), x),
                    "Number of rounds must be an integer.",
                ),
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers

    def calculate_indices(self):
        return set.intersection(
            *[
                {
                    ind
                    for ind, val in self.vocabulary[lang].items()
                    if not (isinstance(val, float) and np.isnan(val))
                }
                for lang in [self.source_lang, self.reply_lang]
            ]
        )

    def play_game(self) -> None:
        self.available_indices = self.calculate_indices()
        for round_ in range(1, self.n_rounds):
            try:
                self.play_round()
            except KeyboardInterrupt:
                store_result = inquirer.confirm(
                    message="Game interrupted with the keyboard. Would you like to save your score nevertheless?",
                    default=True,
                )
                if store_result:
                    self.store_result()
                return None

    def play_round(self) -> None:
        pass  # TODO

    def store_result(self) -> None:
        pass  # TODO