import re
from typing import Callable, Dict

import inquirer
from inquirer import errors

from spanish_game.definitions import LANGUAGES
from spanish_game.exceptions import GameStoppedError, PasswordRetriesLimitError
from spanish_game.round import GameRound
from spanish_game.user import AnonUser, User
from spanish_game.vocabulary import Vocabulary


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
        self.vocabulary.select_languages(
            input_lang=inquiry["source_lang"], output_lang=inquiry["reply_lang"]
        )
        self.n_rounds = self.calculate_rounds(int(inquiry["n_rounds"]))
        self.score = 0
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
        if self.mistakes and inquirer.confirm(
            message="Would you like to start a new game, practicing only on your mistakes?",
            default=False,
        ):
            self.reset_game()
            self.play_game()

    def play_round(self) -> None:
        r = GameRound(self)
        try:
            r.play_round()
            self.score += r.score
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
        self.final_score = round(self.score / self.rounds_played, 4)
        print(
            f"\nThanks for playing, {self.username}! The total score is: {self.score} on {self.rounds_played} rounds played. Your final score is {self.final_score}!"
        )

    def welcome_user(self) -> None:
        print("\n")
        return inquirer.confirm(
            f"Are you ready to start playing?",
            default=True,
        )

    def reset_game(self) -> None:
        self.n_rounds = len(self.mistakes)
        self.vocabulary.reset_vocabulary(keep_languages=True)
        self.vocabulary.select_index(self.mistakes)
        self.score = 0
        self.rounds_played = 0
        self.mistakes = set()
