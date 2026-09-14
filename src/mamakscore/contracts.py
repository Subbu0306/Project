"""Versioned public and internal data contracts."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Strict = ConfigDict(extra="forbid")
Severity = Literal["low", "medium", "high", "critical"]


class SourceFile(BaseModel):
    model_config = Strict
    name: str = Field(min_length=1, max_length=255)
    media_type: str
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class PageDiagnostic(BaseModel):
    model_config = Strict
    page: int = Field(ge=1)
    method: Literal["direct", "vision", "empty"]
    characters: int = Field(ge=0)
    alphanumeric_ratio: float = Field(ge=0, le=1)
    printable_ratio: float = Field(ge=0, le=1)


class ExtractionResult(BaseModel):
    model_config = Strict
    source: SourceFile
    method: Literal["direct", "vision", "hybrid"]
    page_count: int = Field(ge=1)
    canonical_text: str = Field(min_length=1)
    pages: list[PageDiagnostic]
    text_characters: int = Field(ge=1)


class FinancialInput(BaseModel):
    model_config = Strict
    name: str
    value: Decimal
    period: Literal["monthly", "annual", "point_in_time", "unknown"] = "unknown"
    currency: str | None = None
    source: str


class FinancialMetric(BaseModel):
    model_config = Strict
    name: str
    value: Decimal | None = None
    unit: str
    formula: str
    source_inputs: list[str] = Field(default_factory=list)
    unavailable_reason: str | None = None


class FinancialResult(BaseModel):
    model_config = Strict
    provided: bool
    model_family: Literal["startup", "simple_sme", "investor", "unknown", "none"]
    inputs: dict[str, FinancialInput] = Field(default_factory=dict)
    metrics: dict[str, FinancialMetric] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    canonical_text: str = ""


class CriterionScore(BaseModel):
    model_config = Strict
    criterion_id: str
    score: int = Field(ge=0, le=10)
    justification: str = Field(min_length=1, max_length=4000)
    evidence_quote: str = Field(max_length=4000)
    source_file: str = Field(min_length=1, max_length=255)
    confidence: Literal["high", "medium", "low"]


class RedFlag(BaseModel):
    model_config = Strict
    flag_type: Literal[
        "unsupported_claim",
        "unrealistic_assumption",
        "contradiction",
        "missing_information",
        "circular_reasoning",
    ]
    severity: Severity
    summary: str = Field(min_length=1, max_length=2000)
    evidence_quote: str = Field(default="", max_length=4000)
    source_file: str | None = Field(default=None, max_length=255)
    criterion_ids: list[str] = Field(default_factory=list)
    claimed_value: Decimal | None = None
    computed_metric: str | None = None
    relative_difference: Decimal | None = None


class InvestorQuestion(BaseModel):
    model_config = Strict
    question: str = Field(min_length=1, max_length=1000)
    criterion_ids: list[str] = Field(min_length=1)
    evidence_quote: str = Field(default="", max_length=4000)


class ImprovementActionDraft(BaseModel):
    model_config = Strict
    action: str = Field(min_length=1, max_length=2000)
    criterion_id: str
    target_score: int = Field(ge=0, le=10)
    priority: Literal["high", "medium", "low"]


class ImprovementAction(ImprovementActionDraft):
    projected_gain: Decimal = Field(ge=0, le=100)


class ConfidenceResult(BaseModel):
    model_config = Strict
    value: float | None = Field(default=None, ge=0, le=100)
    status: Literal["PROVISIONAL_NOT_CLIENT_APPROVED"] = "PROVISIONAL_NOT_CLIENT_APPROVED"
    client_approved: Literal[False] = False
    formula_version: str
    components: dict[str, float | int]


class BandResult(BaseModel):
    model_config = Strict
    label: str
    boundary_escalation: bool
    human_review_required: Literal[True] = True


class Timing(BaseModel):
    model_config = Strict
    extraction_seconds: float = Field(ge=0)
    provider_seconds: float = Field(ge=0)
    total_seconds: float = Field(ge=0)


class Provenance(BaseModel):
    model_config = Strict
    provider: str
    model_id: str
    rubric_version: str
    rubric_digest: str
    prompt_version: str
    prompt_digest: str
    input_digest: str
    confidence_formula_version: str
    from_cache: bool = False
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    estimated_cost_usd: Decimal | None = Field(default=None, ge=0)


class AssessmentDraft(BaseModel):
    model_config = Strict
    criterion_scores: list[CriterionScore]
    red_flags: list[RedFlag] = Field(default_factory=list)
    investor_questions: list[InvestorQuestion]
    improvement_actions: list[ImprovementActionDraft] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


class AssessmentResult(BaseModel):
    model_config = Strict
    application_id: str
    source_files: list[SourceFile]
    extraction: ExtractionResult
    financials: FinancialResult
    criterion_scores: list[CriterionScore]
    mamak_score: Decimal = Field(ge=0, le=100)
    band: BandResult
    mamak_confidence: ConfidenceResult
    red_flags: list[RedFlag]
    investor_questions: list[InvestorQuestion] = Field(min_length=5, max_length=10)
    improvement_plan: list[ImprovementAction]
    missing_information: list[str]
    report_html: str
    provenance: Provenance
    timing: Timing


class EvaluationEnvelope(BaseModel):
    model_config = Strict
    api_version: Literal["1.0"] = "1.0"
    request_id: str
    generated_at: datetime
    assessment: AssessmentResult


class ErrorDetail(BaseModel):
    model_config = Strict
    code: str
    message: str
    field: str | None = None
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    model_config = Strict
    api_version: Literal["1.0"] = "1.0"
    request_id: str
    generated_at: datetime
    error: ErrorDetail


class AssessmentSummary(BaseModel):
    model_config = Strict
    application_id: str
    rubric_version: str
    rubric_digest: str
    criterion_scores: list[CriterionScore]
    mamak_score: Decimal = Field(ge=0, le=100)
    band: str
    missing_information: list[str] = Field(default_factory=list)


class ComparisonRequest(BaseModel):
    model_config = Strict
    previous: AssessmentSummary
    current: AssessmentSummary


class CategoryMovement(BaseModel):
    model_config = Strict
    criterion_id: str
    previous_score: int
    current_score: int
    delta: int


class ComparisonResult(BaseModel):
    model_config = Strict
    application_id: str
    comparable: bool
    warning: str | None = None
    categories: list[CategoryMovement]
    previous_mamak_score: Decimal
    current_mamak_score: Decimal
    mamak_score_delta: Decimal
    previous_band: str
    current_band: str
    resolved_missing_information: list[str]
    new_missing_information: list[str]
