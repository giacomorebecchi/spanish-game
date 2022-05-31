import random
import re
from typing import Callable, Dict, List

import inquirer
import numpy as np
from inquirer import errors

from spanish_game import settings
from spanish_game.data import load_vocabulary
from spanish_game.definitions import LANGUAGES
from spanish_game.match_strings import strings_score


class Game:
    def __init__(self) -> None:
        self.vocabulary = load_vocabulary()
        self.available_langs = LANGUAGES
        inquiry = self._inquire()
        self.username = inquiry["username"]
        self.source_lang = inquiry["source_lang"]
        self.reply_lang = inquiry["reply_lang"]
        self.available_indices = self.calculate_indices()
        self.n_rounds = min(len(self.available_indices), int(inquiry["n_rounds"]))
        self.score = 0
        self.settings = settings.get_settings()
        self.rounds_played = 0
        self.mistakes = []
        self.play_game()

    def inquire_validator(
        self, answers: Dict[str, str], current: str, validate: Callable, message: str
    ) -> bool:
        if validate(answers, current):
            return True
        else:
            raise errors.ValidationError(current, message)

    def _inquire(self) -> Dict[str, str]:
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
                    lambda _, x: re.match(re.compile(r"[0-9]+"), x),
                    "Number of rounds must be an integer.",
                ),
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers

    def calculate_indices(self) -> List:
        indices = list(
            set.intersection(
                *[
                    {
                        ind
                        for ind, val in self.vocabulary[lang].items()
                        if not (isinstance(val, float) and np.isnan(val))
                    }
                    for lang in [self.source_lang, self.reply_lang]
                ]
            )
        )
        random.shuffle(indices)
        return indices

    def play_game(self) -> None:
        self.welcome_user()
        for _ in range(self.n_rounds):
            try:
                self.play_round()
                self.rounds_played += 1
            except KeyboardInterrupt:
                if self.rounds_played:
                    store_score = inquirer.confirm(
                        message="Game interrupted with the keyboard. Would you like to save your score nevertheless?",
                        default=True,
                    )
                    if store_score:
                        self.store_score()
                else:
                    print("You have closed the game successfully. Have a nice day!")
                return None
        self.store_score()
        if self.mistakes and inquirer.confirm(
            message="Would you like to start a new game, practicing only on your mistakes?",
            default=True,
        ):
            self.reset_game()
            self.play_game()

    def play_round(self) -> None:
        index = self.available_indices.pop()
        word = self.vocabulary[self.source_lang][index]
        solution = self.vocabulary[self.reply_lang][index].lower()
        # TODO: Handle multpile solutions
        # TODO: Handle accents
        answer = input(f"\n{word}: ").lower()
        if solution == answer:
            print("Correct!")
            self.score += self.settings.SCORE_ROUND
        else:
            self.mistakes.append(index)
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
            skipchar=self.settings.SKIP_CHARACTER,
        )
        print("-" * (10 + len(a1)))
        print(f"Performed match:\nAnswer:   {b1}\nSolution: {a1}")
        print("-" * (10 + len(a1)))
        round_score = max(0, 10 - optcost)
        return round_score

    def store_score(self) -> None:
        self.final_score = round(self.score / self.rounds_played, 4)
        print(
            f"\nThanks for playing, {self.username}! The total score is: {self.score} on {self.rounds_played} rounds played. Your final score is {self.final_score}!"
        )

    def welcome_user(self) -> None:
        print("\n")
        inquirer.confirm(
            f"Hi {self.username}, thanks for playing! Are you ready to start?",
            default=True,
        )

    def reset_game(self) -> None:
        self.n_rounds = len(self.mistakes)
        self.available_indices = self.mistakes.copy()
        random.shuffle(self.available_indices)
        self.score = 0
        self.rounds_played = 0
        self.mistakes = []
