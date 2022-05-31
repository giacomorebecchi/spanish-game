from spanish_game.settings import get_settings


def test_get_settings() -> None:
    settings = get_settings()
    assert isinstance(settings.COST_MISALIGNMENT, float)
    assert isinstance(settings.COST_SKIP, float)
    assert isinstance(settings.SCORE_ROUND, float)
    assert isinstance(settings.SKIP_CHARACTER, str)
