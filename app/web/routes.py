from __future__ import annotations

from datetime import date

import plotly.graph_objects as go
from flask import Blueprint, current_app, redirect, render_template, request, url_for

from app.domain.models import DailyEntry

web_bp = Blueprint("web", __name__)

FOOD_PRESETS = ["цитрусы", "острое", "сладкое", "молочное", "кофе"]
CONTACT_PRESETS = ["бытовая химия", "перчатки", "мыло", "металл", "косметика"]
GI_PRESETS = ["вздутие", "боль", "тошнота", "изжога", "неустойчивый стул"]
LOCATION_PRESETS = ["ладони", "пальцы", "стопы", "запястья", "другое"]


@web_bp.get("/")
def dashboard():
    repo = current_app.config["repository"]
    analytics = current_app.config["analytics"]
    entries = repo.list_entries()
    report = analytics.build_report()
    return render_template("dashboard.html", entries=entries[:7], report=report)


@web_bp.route("/entries/new", methods=["GET", "POST"])
def new_entry():
    repo = current_app.config["repository"]
    if request.method == "POST":
        entry = _entry_from_form(request.form)
        repo.upsert_entry(entry)
        return redirect(url_for("web.history", saved=1))

    return render_template(
        "entry_form.html",
        food_presets=FOOD_PRESETS,
        contact_presets=CONTACT_PRESETS,
        gi_presets=GI_PRESETS,
        location_presets=LOCATION_PRESETS,
        today=date.today().isoformat(),
    )


@web_bp.get("/history")
def history():
    repo = current_app.config["repository"]
    saved = request.args.get("saved")
    entries = repo.list_entries()
    return render_template("history.html", entries=entries, saved=saved)


@web_bp.get("/analytics")
def analytics():
    analytics_service = current_app.config["analytics"]
    report = analytics_service.build_report()

    top = [x for x in report.trigger_scores if x.score > 0][:10]
    if top:
        fig = go.Figure(
            go.Bar(
                x=[x.score for x in top],
                y=[x.factor for x in top],
                orientation="h",
                marker_color="#2563eb",
            )
        )
        fig.update_layout(
            title="Предполагаемые триггеры (score)",
            xaxis_title="Частота в ухудшениях - частота в обычных днях",
            yaxis_title="Фактор",
            template="plotly_white",
            margin=dict(l=20, r=20, t=60, b=20),
            height=420,
        )
        chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    else:
        chart_html = "<p>Пока недостаточно данных для графика.</p>"

    return render_template("analytics.html", report=report, chart_html=chart_html)


def _entry_from_form(form) -> DailyEntry:
    def as_int(name: str, default: int = 0) -> int:
        raw = form.get(name, "").strip()
        return int(raw) if raw else default

    def as_bool(name: str) -> bool:
        return form.get(name) == "on"

    def as_list(name: str) -> list[str]:
        return form.getlist(name)

    def custom_values(name: str) -> list[str]:
        raw = [x.strip() for x in form.get(name, "").split(",") if x.strip()]
        return [f"custom:{x}" for x in raw]

    photos = [x.strip() for x in form.get("photo_paths", "").splitlines() if x.strip()]

    return DailyEntry(
        id=None,
        entry_date=date.fromisoformat(form["entry_date"]),
        rash_present=as_bool("rash_present"),
        severity=as_int("severity"),
        itch=as_int("itch"),
        burning=as_int("burning"),
        dryness=as_int("dryness"),
        location=as_list("location"),
        comment=form.get("comment", "").strip(),
        stress_level=as_int("stress_level"),
        strong_stress=as_bool("strong_stress"),
        sleep_hours=as_int("sleep_hours", 7),
        sleep_quality=as_int("sleep_quality"),
        wellbeing=as_int("wellbeing"),
        sweating=as_int("sweating"),
        heat=as_bool("heat"),
        wet_skin=as_bool("wet_skin"),
        friction=as_bool("friction"),
        gi_issues=as_bool("gi_issues"),
        gi_severity=as_int("gi_severity"),
        gi_symptoms=as_list("gi_symptoms"),
        gi_comment=form.get("gi_comment", "").strip(),
        food_triggers=as_list("food_triggers") + custom_values("food_custom"),
        contact_triggers=as_list("contact_triggers") + custom_values("contact_custom"),
        moisturizer=as_bool("moisturizer"),
        medication=as_bool("medication"),
        antihistamines=as_bool("antihistamines"),
        steroids=as_bool("steroids"),
        treatment_other=form.get("treatment_other", "").strip(),
        photos=photos,
        day_result=form.get("day_result", "neutral"),
    )
