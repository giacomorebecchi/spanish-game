import re
from typing import Callable, Dict, List

import inquirer
import numpy as np
from inquirer import errors

from .definitions import LANGUAGES
from .exceptions import GameStoppedError, PasswordRetriesLimitError
from .game_mode import Mode
from .round import GameRound
from .user import AnonUser, User
from .vocabulary import Vocabulary


class Game:
    def __init__(self) -> None:
        self.vocabulary = Vocabulary()
        self.available_langs = LANGUAGES
        self.username = self._inquire_username()
        try:
            self.user = User(self.username)
        except PasswordRetriesLimitError:
            if inquirer.confirm(
                "The login was not successful. Would you like to play anonymously?",
                default=True,
            ):
                self.user = AnonUser()
            else:
                print("No problem. Good bye!")
                self.user = None
                return None
        inquiry = self._inquire()
        self.mistakes = set()
        self.input_lang = inquiry["source_lang"]
        self.output_lang = inquiry["reply_lang"]
        self.vocabulary.select_languages(
            input_lang=self.input_lang, output_lang=self.output_lang
        )
        self.modes = self.calculate_modes()
        self.vocabulary.select_modes(self.modes)
        self.n_rounds = self.calculate_rounds(int(inquiry["n_rounds"]))
        self.score_ar = np.zeros(self.n_rounds)
        self.rounds_played = 0

    def calculate_rounds(self, n_rounds: str) -> int:
        len_voc = len(self.vocabulary)
        if 0 < n_rounds <= len_voc:
            return n_rounds
        elif n_rounds == 0:
            print(
                f"You will play as many rounds as the length of the vocabulary ({len_voc})!"
            )
            return len_voc
        else:
            print(f"Our vocabulary is shorter! You will play {len_voc} rounds")
            return len_voc

    def calculate_modes(self) -> Dict[str, List[int]]:
        modes = self.user.data.get_modes_indices(self.input_lang, self.output_lang)
        return self._inquire_modes(modes)

    def inquire_validator(
        self, answers: Dict[str, str], current: str, validate: Callable, message: str
    ) -> bool:
        if validate(answers, current):
            return True
        else:
            raise errors.ValidationError(current, message)

    def _inquire(self) -> Dict[str, str]:
        questions = [
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
                message="How many rounds would you like to play? (0 to play the whole vocabulary)",
                validate=lambda answers, current: self.inquire_validator(
                    answers,
                    current,
                    lambda _, x: re.match(re.compile(r"[0-9]+"), x),
                    "Number of rounds must be an integer.",
                ),
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers

    def _inquire_username(self) -> str:
        questions = [
            inquirer.Text(
                name="username",
                message="Input your username",
                # default="anonUser",
                validate=lambda answers, current: self.inquire_validator(
                    answers,
                    current,
                    lambda _, x: re.match(re.compile(r"[a-zA-Z0-9]{4,12}"), x),
                    "Username must be only formed by letters or numbers, length of 4 to 12.",
                ),
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers["username"]

    def _inquire_modes(self, modes: List[Mode]) -> List[str]:
        questions = [
            inquirer.Checkbox(
                name="modes",
                message="Which modality of game would you like to play?",
                choices=modes,
                carousel=True,
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers["modes"]

    def play_game(self) -> None:
        if self.user is None:
            return None
        if not self.welcome_user():
            print("No problem. See you later!")
            return None
        for _ in range(self.n_rounds):
            try:
                self.play_round()
                self.rounds_played += 1
            except GameStoppedError:
                return None
        self.store_score()

    def play_round(self) -> None:
        r = GameRound(self)
        try:
            r.play_round()
            self.score_ar[self.rounds_played] = r.score

            if not r.correct:
                self.mistakes.add(r.index)
        except (KeyboardInterrupt, EOFError):
            if inquirer.confirm(
                "Game paused. Would you like to continue playing?", default=True
            ):
                return self.play_round()
            else:
                if self.rounds_played and inquirer.confirm(
                    "Game stopped. Would you like to store your score?", default=True
                ):
                    self.store_score()
                else:
                    print(f"Thanks for playing, {self.username}!")
                raise GameStoppedError

    def store_score(self) -> None:
        tot_score = self.score_ar.sum()
        self.result = self.vocabulary.get_ids(self.rounds_played)
        for i, d in enumerate(self.result):
            d["score"] = self.score_ar[i]
        self.user.data.update_game_result(
            self.input_lang, self.output_lang, self.result
        )
        self.user.write_user_data()
        self.final_score = round(tot_score / self.rounds_played, 4)
        print(
            f"\nThanks for playing, {self.username}! The total score is: {tot_score} on {self.rounds_played} rounds played. Your final score is {self.final_score}!"
        )

    def welcome_user(self) -> None:
        print("\n")
        return inquirer.confirm(
            f"Are you ready to start playing?",
            default=True,
        )
