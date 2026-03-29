from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_date TEXT NOT NULL UNIQUE,
                    rash_present INTEGER NOT NULL,
                    severity INTEGER NOT NULL,
                    itch INTEGER NOT NULL,
                    burning INTEGER NOT NULL,
                    dryness INTEGER NOT NULL,
                    location TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    stress_level INTEGER NOT NULL,
                    strong_stress INTEGER NOT NULL,
                    sleep_hours INTEGER NOT NULL,
                    sleep_quality INTEGER NOT NULL,
                    wellbeing INTEGER NOT NULL,
                    sweating INTEGER NOT NULL,
                    heat INTEGER NOT NULL,
                    wet_skin INTEGER NOT NULL,
                    friction INTEGER NOT NULL,
                    gi_issues INTEGER NOT NULL,
                    gi_severity INTEGER NOT NULL,
                    gi_symptoms TEXT NOT NULL,
                    gi_comment TEXT NOT NULL,
                    moisturizer INTEGER NOT NULL,
                    medication INTEGER NOT NULL,
                    antihistamines INTEGER NOT NULL,
                    steroids INTEGER NOT NULL,
                    treatment_other TEXT NOT NULL,
                    day_result TEXT NOT NULL CHECK(day_result in ('worsening', 'neutral', 'improvement', 'remission'))
                );

                CREATE TABLE IF NOT EXISTS triggers_food (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id INTEGER NOT NULL,
                    trigger_name TEXT NOT NULL,
                    is_custom INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS triggers_contact (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id INTEGER NOT NULL,
                    trigger_name TEXT NOT NULL,
                    is_custom INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS custom_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_type TEXT NOT NULL CHECK(trigger_type in ('food', 'contact')),
                    trigger_name TEXT NOT NULL UNIQUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS symptoms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id INTEGER NOT NULL,
                    symptom_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
                );
                """
            )
