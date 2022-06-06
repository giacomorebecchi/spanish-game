from typing import Set, Tuple

import pandas as pd

from spanish_game.definitions import LANGUAGES, VOCABULARY_FILE


class Vocabulary:
    def __init__(self):
        self.raw_df = pd.read_excel(VOCABULARY_FILE, sheet_name="Sheet1")
        self.available_languages = LANGUAGES
        self.validate_vocabulary()
        self.df = self.raw_df.sample(frac=1)

    def reset_vocabulary(self, keep_languages: bool = True) -> None:
        self.df = self.raw_df.sample(frac=1)
        if keep_languages:
            self.select_languages()

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, key: int) -> Tuple[str, str]:
        index = self.df.index[key]
        return (
            self.df.loc[index, self.input_lang],
            self.df.loc[index, self.output_lang].lower(),
        )

    def get_index(self, key: int) -> int:
        return self.df.index[key]

    def validate_vocabulary(self) -> None:
        diff = set.difference(set(self.raw_df.columns), self.available_languages)
        if diff:
            raise Exception("Vocabulary file does not contain languages {diff}.")

    def select_languages(
        self, input_lang: str | None = None, output_lang: str | None = None
    ) -> None:
        if input_lang is not None:
            self.input_lang = input_lang
        if output_lang is not None:
            self.output_lang = output_lang
        self.df = self.df.loc[:, [self.input_lang, self.output_lang]]
        self.df.dropna(axis=0, inplace=True)

    def select_categories(self, categories: Set = None):
        pass  # TODO

    def select_index(self, index: int | Set[int]) -> None:
        self.df = self.df.loc[list(index), :]
