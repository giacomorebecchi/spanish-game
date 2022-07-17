from __future__ import annotations

from typing import TYPE_CHECKING

from .definitions import ACCENT_EQUIVALENTS
from .match_strings import strings_score
from .settings import get_settings

if TYPE_CHECKING:
    from spanish_game.game import Game


class GameRound:
    def __init__(self, game: Game) -> None:
        self.round = game.rounds_played
        self.vocabulary = game.vocabulary
        self.index = game.rounds_played
        self.settings = get_settings()
        self.score = self.settings.SCORE_ROUND

    def play_round(self) -> float:
        word, solution = self.vocabulary[self.index]
        # TODO: Handle multiple solutions
        answer = self.ask_answer(word)
        if solution == answer:
            self.correct = True
            print("Correct!")
        elif self.difference_only_accents(answer, solution):
            self.correct = False
            print(
                f"Almost! Just check the accents for a perfect answer. The correct accentuation is: {solution}"
            )
            penalty = sum(
                [
                    self.settings.COST_ACCENT if x != y else 0
                    for x, y in zip(answer, solution)
                ]
            )
            self.score = max(0, self.score - penalty)
        else:
            self.correct = False
            if not answer:
                print(f"The correct answer is: {solution.capitalize()}")
                self.score = 0
            else:
                self.calculate_score(solution, answer)
                print(f"Wrong! The correct answer was: {solution.capitalize()}")
        print(f"Points earned: {self.score}")

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
        self.score = max(0, self.score - optcost)

    def ask_answer(self, word: str) -> str:
        return input(f"\n{word}: ").lower()

    def difference_only_accents(self, w1: str, w2: str) -> bool:
        if len(w1) != len(w2):
            return False
        else:
            for c1, c2 in zip(w1, w2):
                if not (c1 == c2 or c1 in ACCENT_EQUIVALENTS.get(c2, {})):
                    return False
            return True
