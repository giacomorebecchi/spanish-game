from pydantic import BaseModel, validator

from spanish_game import config


class Settings(BaseModel):
    COST_SKIP: float = config.COST_SKIP
    COST_MISALIGNMENT: float = config.COST_MISALIGNMENT
    COST_ACCENT: float = config.COST_ACCENT
    SCORE_ROUND: float = config.SCORE_ROUND
    SKIP_CHARACTER: str = config.SKIP_CHARACTER

    @validator("SCORE_ROUND")
    def score(cls, v, values, **kwargs):
        if v <= max(values["COST_SKIP"], values["COST_MISALIGNMENT"]):
            raise ValueError(
                "Score provided by each round is lower than the cost of a single mistake!"
            )
        return v


def get_settings(**kwargs):
    return Settings(**kwargs)
