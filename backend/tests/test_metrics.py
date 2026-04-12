from evaluation.metrics import heuristic_quality_score


def test_quality_score_is_bounded() -> None:
    assert 0.0 <= heuristic_quality_score("short answer") <= 1.0


def test_quality_score_rewards_context_overlap() -> None:
    answer = "Company revenue guidance improved after acquisition."
    low = heuristic_quality_score(answer, ["completely unrelated text"])
    high = heuristic_quality_score(answer, ["revenue guidance improved after acquisition"])
    assert high >= low
