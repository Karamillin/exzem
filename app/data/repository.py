from __future__ import annotations

import json
from datetime import date
from typing import Iterable

from app.data.database import Database
from app.domain.models import DailyEntry


class EntryRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def upsert_entry(self, entry: DailyEntry) -> int:
        with self.db.connect() as conn:
            existing = conn.execute(
                "SELECT id FROM entries WHERE entry_date = ?", (entry.entry_date.isoformat(),)
            ).fetchone()

            if existing:
                entry_id = int(existing["id"])
                conn.execute(
                    """
                    UPDATE entries SET
                        rash_present=?, severity=?, itch=?, burning=?, dryness=?,
                        location=?, comment=?, stress_level=?, strong_stress=?, sleep_hours=?,
                        sleep_quality=?, wellbeing=?, sweating=?, heat=?, wet_skin=?, friction=?,
                        gi_issues=?, gi_severity=?, gi_symptoms=?, gi_comment=?,
                        moisturizer=?, medication=?, antihistamines=?, steroids=?, treatment_other=?, day_result=?
                    WHERE id=?
                    """,
                    self._entry_values(entry) + [entry_id],
                )
                self._replace_child_tables(conn, entry_id, entry)
                return entry_id

            cursor = conn.execute(
                """
                INSERT INTO entries (
                    entry_date, rash_present, severity, itch, burning, dryness,
                    location, comment, stress_level, strong_stress, sleep_hours,
                    sleep_quality, wellbeing, sweating, heat, wet_skin, friction,
                    gi_issues, gi_severity, gi_symptoms, gi_comment,
                    moisturizer, medication, antihistamines, steroids, treatment_other, day_result
                ) VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """,
                [entry.entry_date.isoformat(), *self._entry_values(entry)],
            )
            entry_id = int(cursor.lastrowid)
            self._replace_child_tables(conn, entry_id, entry)
            return entry_id

    def list_entries(self) -> list[DailyEntry]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM entries ORDER BY entry_date DESC").fetchall()
            return [self._build_entry(conn, row) for row in rows]

    def get_entry_by_date(self, entry_date: date) -> DailyEntry | None:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM entries WHERE entry_date = ?", (entry_date.isoformat(),)
            ).fetchone()
            if not row:
                return None
            return self._build_entry(conn, row)

    def _build_entry(self, conn, row) -> DailyEntry:
        entry_id = int(row["id"])
        food = self._child_values(conn, "triggers_food", entry_id)
        contact = self._child_values(conn, "triggers_contact", entry_id)
        photos = self._photo_values(conn, entry_id)

        return DailyEntry(
            id=entry_id,
            entry_date=date.fromisoformat(row["entry_date"]),
            rash_present=bool(row["rash_present"]),
            severity=int(row["severity"]),
            itch=int(row["itch"]),
            burning=int(row["burning"]),
            dryness=int(row["dryness"]),
            location=json.loads(row["location"]),
            comment=row["comment"],
            stress_level=int(row["stress_level"]),
            strong_stress=bool(row["strong_stress"]),
            sleep_hours=int(row["sleep_hours"]),
            sleep_quality=int(row["sleep_quality"]),
            wellbeing=int(row["wellbeing"]),
            sweating=int(row["sweating"]),
            heat=bool(row["heat"]),
            wet_skin=bool(row["wet_skin"]),
            friction=bool(row["friction"]),
            gi_issues=bool(row["gi_issues"]),
            gi_severity=int(row["gi_severity"]),
            gi_symptoms=json.loads(row["gi_symptoms"]),
            gi_comment=row["gi_comment"],
            food_triggers=food,
            contact_triggers=contact,
            moisturizer=bool(row["moisturizer"]),
            medication=bool(row["medication"]),
            antihistamines=bool(row["antihistamines"]),
            steroids=bool(row["steroids"]),
            treatment_other=row["treatment_other"],
            photos=photos,
            day_result=row["day_result"],
        )

    def _entry_values(self, entry: DailyEntry) -> list:
        return [
            int(entry.rash_present),
            entry.severity,
            entry.itch,
            entry.burning,
            entry.dryness,
            json.dumps(entry.location, ensure_ascii=False),
            entry.comment,
            entry.stress_level,
            int(entry.strong_stress),
            entry.sleep_hours,
            entry.sleep_quality,
            entry.wellbeing,
            entry.sweating,
            int(entry.heat),
            int(entry.wet_skin),
            int(entry.friction),
            int(entry.gi_issues),
            entry.gi_severity,
            json.dumps(entry.gi_symptoms, ensure_ascii=False),
            entry.gi_comment,
            int(entry.moisturizer),
            int(entry.medication),
            int(entry.antihistamines),
            int(entry.steroids),
            entry.treatment_other,
            entry.day_result,
        ]

    def _replace_child_tables(self, conn, entry_id: int, entry: DailyEntry) -> None:
        conn.execute("DELETE FROM triggers_food WHERE entry_id = ?", (entry_id,))
        conn.execute("DELETE FROM triggers_contact WHERE entry_id = ?", (entry_id,))
        conn.execute("DELETE FROM photos WHERE entry_id = ?", (entry_id,))

        self._insert_values(conn, "triggers_food", entry_id, entry.food_triggers)
        self._insert_values(conn, "triggers_contact", entry_id, entry.contact_triggers)

        for photo in entry.photos:
            conn.execute("INSERT INTO photos(entry_id, file_path) VALUES(?, ?)", (entry_id, photo))

        for trigger in self._only_custom(entry.food_triggers):
            conn.execute(
                "INSERT OR IGNORE INTO custom_triggers(trigger_type, trigger_name) VALUES('food', ?)",
                (trigger,),
            )
        for trigger in self._only_custom(entry.contact_triggers):
            conn.execute(
                "INSERT OR IGNORE INTO custom_triggers(trigger_type, trigger_name) VALUES('contact', ?)",
                (trigger,),
            )

    def _insert_values(self, conn, table: str, entry_id: int, values: Iterable[str]) -> None:
        for value in values:
            conn.execute(
                f"INSERT INTO {table}(entry_id, trigger_name, is_custom) VALUES(?, ?, ?)",
                (entry_id, value, int(value.startswith("custom:"))),
            )

    def _child_values(self, conn, table: str, entry_id: int) -> list[str]:
        rows = conn.execute(
            f"SELECT trigger_name FROM {table} WHERE entry_id = ? ORDER BY id", (entry_id,)
        ).fetchall()
        return [r["trigger_name"] for r in rows]

    def _photo_values(self, conn, entry_id: int) -> list[str]:
        rows = conn.execute(
            "SELECT file_path FROM photos WHERE entry_id = ? ORDER BY id", (entry_id,)
        ).fetchall()
        return [r["file_path"] for r in rows]

    def _only_custom(self, values: list[str]) -> list[str]:
        return [value.replace("custom:", "", 1) for value in values if value.startswith("custom:")]
