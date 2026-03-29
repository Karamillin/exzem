from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class DailyEntry:
    entry_date: date
    rash_present: bool
    severity: int
    itch: int
    burning: int
    dryness: int
    location: list[str]
    comment: str
    stress_level: int
    strong_stress: bool
    sleep_hours: int
    sleep_quality: int
    wellbeing: int
    sweating: int
    heat: bool
    wet_skin: bool
    friction: bool
    gi_issues: bool
    gi_severity: int
    gi_symptoms: list[str]
    gi_comment: str
    food_triggers: list[str]
    contact_triggers: list[str]
    moisturizer: bool
    medication: bool
    antihistamines: bool
    steroids: bool
    treatment_other: str
    photos: list[str]
    day_result: str
    id: int | None = None


@dataclass(slots=True)
class TriggerScore:
    factor: str
    worsening_frequency: float
    normal_frequency: float
    score: float
    relation: str


@dataclass(slots=True)
class AnalyticsReport:
    total_entries: int
    worsening_days: int
    normal_days: int
    improving_days: int
    trigger_scores: list[TriggerScore] = field(default_factory=list)
    worsening_explanation: str = ""
    improvement_explanation: str = ""
