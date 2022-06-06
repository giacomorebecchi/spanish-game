import re
from typing import Callable, Dict

import inquirer
from inquirer import errors

from spanish_game import settings
from spanish_game.definitions import ACCENT_EQUIVALENTS, LANGUAGES
from spanish_game.exceptions import GameStoppedError, PasswordRetriesLimitError
from spanish_game.match_strings import strings_score
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
        self.source_lang = inquiry["source_lang"]
        self.reply_lang = inquiry["reply_lang"]
        self.mistakes = set()
        self.vocabulary.select_languages(
            input_lang=self.source_lang, output_lang=self.reply_lang
        )
        self.n_rounds = self.calculate_rounds(int(inquiry["n_rounds"]))
        self.score = 0
        self.settings = settings.get_settings()
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

    def ask_answer(self, word: str) -> str:
        try:
            return input(f"\n{word}: ").lower()
        except (KeyboardInterrupt, EOFError):
            if inquirer.confirm(
                "Game paused. Would you like to continue playing?", default=True
            ):
                return self.ask_answer(word)
            else:
                if self.rounds_played and inquirer.confirm(
                    "Game stopped. Would you like to store your score?", default=True
                ):
                    self.store_score()
                else:
                    print(f"Thanks for playing, {self.username}!")
                raise GameStoppedError

    def play_round(self) -> None:
        index = self.vocabulary.get_index(self.rounds_played)
        word, solution = self.vocabulary[self.rounds_played]
        # TODO: Handle multiple solutions
        answer = self.ask_answer(word)
        if solution == answer:
            print("Correct!")
            self.score += self.settings.SCORE_ROUND
        elif self.difference_only_accents(answer, solution):
            self.mistakes.add(index)
            print(
                f"Almost! Just check the accents for a perfect answer. The correct accentuation is: {solution}"
            )
            penalty = sum(
                [
                    self.settings.COST_ACCENT if x != y else 0
                    for x, y in zip(answer, solution)
                ]
            )
            self.score += self.settings.SCORE_ROUND - penalty
        else:
            self.mistakes.add(index)
            if not answer:
                print(f"The correct answer is: {solution.capitalize()}")
            else:
                self.score += self.calculate_score(solution, answer)
                print(f"Wrong! The correct answer was: {solution.capitalize()}")

    def calculate_score(self, solution: str, answer: str):
        optcost, a1, b1, _ = strings_score(
            solution,
            answer,
            c_skip=self.settings.COST_SKIP,
            c_misalignment=self.settings.COST_MISALIGNMENT,
            c_accent=self.settings.COST_ACCENT,
            skipchar=self.settings.SKIP_CHARACTER,
        )
        print("-" * (10 + len(a1)))
        print(f"Performed match:\nAnswer:   {b1}\nSolution: {a1}")
        print("-" * (10 + len(a1)))
        round_score = max(0, 10 - optcost)
        return round_score

    def difference_only_accents(self, w1: str, w2: str) -> bool:
        if len(w1) != len(w2):
            return False
        else:
            for c1, c2 in zip(w1, w2):
                if not (c1 == c2 or c1 in ACCENT_EQUIVALENTS.get(c2, {})):
                    return False
            return True

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
