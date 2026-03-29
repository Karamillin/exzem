from __future__ import annotations

from collections import Counter

from app.data.repository import EntryRepository
from app.domain.models import AnalyticsReport, DailyEntry, TriggerScore


class AnalyticsService:
    FACTOR_LABELS = {
        "high_stress": "высокий стресс",
        "strong_stress": "сильный стресс",
        "high_sweating": "высокая потливость",
        "heat": "жара",
        "wet_skin": "влажная кожа",
        "friction": "трение кожи",
        "gi_issues": "симптомы ЖКТ",
        "poor_sleep": "недостаточный сон",
        "rash_present": "наличие сыпи",
    }

    def __init__(self, repository: EntryRepository) -> None:
        self.repository = repository

    def build_report(self) -> AnalyticsReport:
        entries = self.repository.list_entries()
        worsening = [e for e in entries if e.day_result == "worsening"]
        normal = [e for e in entries if e.day_result in {"neutral", "improvement", "remission"}]
        improving = [e for e in entries if e.day_result in {"improvement", "remission"}]

        factors = self._collect_factors(entries)
        scores: list[TriggerScore] = []
        for factor in sorted(factors):
            w_freq = self._frequency(worsening, factor)
            n_freq = self._frequency(normal, factor)
            score = round(w_freq - n_freq, 3)
            relation = self._classify(score)
            scores.append(TriggerScore(factor, w_freq, n_freq, score, relation))

        scores.sort(key=lambda s: s.score, reverse=True)
        return AnalyticsReport(
            total_entries=len(entries),
            worsening_days=len(worsening),
            normal_days=len(normal),
            improving_days=len(improving),
            trigger_scores=scores,
            worsening_explanation=self._build_worsening_text(scores),
            improvement_explanation=self._build_improvement_text(entries),
        )

    def explain_day(self, entry: DailyEntry) -> str:
        reasons: list[str] = []
        if entry.stress_level >= 7 or entry.strong_stress:
            reasons.append("высокий уровень стресса")
        if entry.sweating >= 7 or entry.heat or entry.wet_skin:
            reasons.append("потливость / тепло / влажная кожа")
        if entry.food_triggers:
            reasons.append("пищевые триггеры")
        if entry.contact_triggers:
            reasons.append("контактные триггеры")
        if entry.gi_issues:
            reasons.append("симптомы ЖКТ")
        if entry.sleep_hours < 6 or entry.sleep_quality <= 4:
            reasons.append("недостаточный сон")

        if not reasons:
            return "Для этого дня нет выраженных факторов риска; возможна комбинация менее явных причин."

        prefix = "Этот день отмечен как ухудшение. Возможные факторы: "
        return prefix + ", ".join(reasons) + "."

    def _collect_factors(self, entries: list[DailyEntry]) -> set[str]:
        factors: set[str] = {
            "high_stress",
            "strong_stress",
            "high_sweating",
            "heat",
            "wet_skin",
            "friction",
            "gi_issues",
            "poor_sleep",
            "rash_present",
        }
        for entry in entries:
            for item in entry.food_triggers:
                factors.add(f"food:{item}")
            for item in entry.contact_triggers:
                factors.add(f"contact:{item}")
        return factors

    def _frequency(self, entries: list[DailyEntry], factor: str) -> float:
        if not entries:
            return 0.0
        hits = sum(1 for e in entries if self._entry_has_factor(e, factor))
        return round(hits / len(entries), 3)

    def _entry_has_factor(self, entry: DailyEntry, factor: str) -> bool:
        checks = {
            "high_stress": entry.stress_level >= 7,
            "strong_stress": entry.strong_stress,
            "high_sweating": entry.sweating >= 7,
            "heat": entry.heat,
            "wet_skin": entry.wet_skin,
            "friction": entry.friction,
            "gi_issues": entry.gi_issues,
            "poor_sleep": entry.sleep_hours < 6 or entry.sleep_quality <= 4,
            "rash_present": entry.rash_present,
        }
        if factor in checks:
            return checks[factor]
        if factor.startswith("food:"):
            return factor.removeprefix("food:") in entry.food_triggers
        if factor.startswith("contact:"):
            return factor.removeprefix("contact:") in entry.contact_triggers
        return False

    def _classify(self, score: float) -> str:
        if score > 0.4:
            return "высокая связь"
        if 0.2 <= score <= 0.4:
            return "средняя связь"
        if 0.1 <= score < 0.2:
            return "слабая связь"
        return "нет явной связи"

    def _build_worsening_text(self, scores: list[TriggerScore]) -> str:
        top = [s for s in scores if s.score >= 0.2][:5]
        if not top:
            return "Недостаточно данных для выделения устойчивых предполагаемых триггеров ухудшения."
        parts = [self._human_factor(t.factor) for t in top]
        return (
            "Возможные причины ухудшения: "
            + ", ".join(parts)
            + ". Эти факторы чаще совпадают с днями ухудшения."
        )

    def _build_improvement_text(self, entries: list[DailyEntry]) -> str:
        improving = [e for e in entries if e.day_result in {"improvement", "remission"}]
        if not improving:
            return "Пока нет дней улучшения/ремиссии для анализа."

        counter = Counter()
        for entry in improving:
            if entry.sleep_hours >= 7:
                counter["достаточный сон"] += 1
            if entry.stress_level <= 4:
                counter["низкий стресс"] += 1
            if not entry.gi_issues:
                counter["без симптомов ЖКТ"] += 1
            if entry.moisturizer:
                counter["регулярное увлажнение"] += 1

        if not counter:
            return "Не найдено повторяющихся факторов улучшения."
        top = ", ".join([k for k, _ in counter.most_common(4)])
        return f"В дни улучшения чаще встречаются: {top}."

    def _human_factor(self, factor: str) -> str:
        if factor.startswith("food:"):
            return f"еда: {factor.removeprefix('food:').replace('custom:', '')}"
        if factor.startswith("contact:"):
            return f"контакт: {factor.removeprefix('contact:').replace('custom:', '')}"
        return self.FACTOR_LABELS.get(factor, factor)
