from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.data.database import Database
from app.data.repository import EntryRepository
from app.services.analytics_service import AnalyticsService
from app.ui.main_window import MainWindow


def build_app() -> QApplication:
    app = QApplication(sys.argv)
    app.setApplicationName("Экзема-трекер")
    app.setOrganizationName("Локально")
    return app


def main() -> int:
    db_path = Path("eczema_tracker.db")
    database = Database(db_path)
    database.initialize()

    repository = EntryRepository(database)
    analytics = AnalyticsService(repository)

    app = build_app()
    window = MainWindow(repository, analytics)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
