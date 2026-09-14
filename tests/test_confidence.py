from mamakscore.confidence import calculate_confidence
from mamakscore.contracts import CriterionScore, RedFlag


def scores(quote):
    return [
        CriterionScore(
            criterion_id=str(i),
            score=7,
            justification="Reason",
            evidence_quote=quote,
            source_file="deck.pdf",
            confidence="high",
        )
        for i in range(9)
    ]


def test_numeric_evidence_reaches_100_before_penalties():
    result = calculate_confidence(
        scores("Survey of 120 customers found 80% agreement."), [], expose=True
    )
    assert result.value == 100.0
    assert result.status == "PROVISIONAL_NOT_CLIENT_APPROVED"
    assert result.client_approved is False


def test_penalties_and_hidden_value():
    flags = [
        RedFlag(flag_type="unsupported_claim", severity=s, summary="x")
        for s in ("low", "medium", "high")
    ]
    result = calculate_confidence(scores("According to research by Acme"), flags, expose=True)
    assert result.value == 80.0
    hidden = calculate_confidence(scores("According to research by Acme"), flags, expose=False)
    assert hidden.value is None and hidden.components["penalty"] == 20


def test_no_evidence_is_zero():
    assert calculate_confidence(scores(""), [], expose=True).value == 0.0
