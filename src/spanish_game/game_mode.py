from typing import Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel

from .settings import get_settings


class Mode(BaseModel):
    name: str
    message: str
    inclusive: bool
    ids: Optional[int]
    score_round = get_settings().SCORE_ROUND

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return self.message

    def _get_indices(
        self, user_data: pd.DataFrame, input_lang: str, output_lang: str
    ) -> None:
        get_col = lambda s: f"{input_lang}-{output_lang}_{s}"
        data = user_data[user_data[get_col("n-rounds")] > 0].copy()
        if self.name == "all":
            self.ids = []
        elif self.name == "new":
            self.ids = data.index.to_list()
        elif self.name == "low-score":
            self.ids = data[
                data[get_col("tot-score")] / data[get_col("n-rounds")]
                < self.score_round * 0.8
            ].index.to_list()
        elif self.name == "last-1-error":
            self.ids = data[
                data[get_col("score-1")] != self.score_round
            ].index.to_list()
        elif self.name == "last-n-error":
            scores = [get_col(f"score-{i+1}") for i in range(5)]  # TODO: Parametrize
            avg_n_score = data[scores].sum(axis=1) / np.minimum(
                data[get_col("n-rounds")], 5  # TODO: parametrize
            )
            self.ids = data[avg_n_score != self.score_round].index.to_list()
