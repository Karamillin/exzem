from __future__ import annotations

from pathlib import Path

from flask import Flask

from app.data.database import Database
from app.data.repository import EntryRepository
from app.services.analytics_service import AnalyticsService


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    db_path = Path("eczema_tracker.db")
    database = Database(db_path)
    database.initialize()

    app.config["repository"] = EntryRepository(database)
    app.config["analytics"] = AnalyticsService(app.config["repository"])

    from app.web.routes import web_bp

    app.register_blueprint(web_bp)
    return app
