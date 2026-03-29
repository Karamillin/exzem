from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import QMainWindow, QTabWidget

from app.data.repository import EntryRepository
from app.services.analytics_service import AnalyticsService
from app.ui.analytics_tab import AnalyticsTab
from app.ui.daily_entry_tab import DailyEntryTab
from app.ui.history_tab import HistoryTab


class MainWindow(QMainWindow):
    def __init__(self, repository: EntryRepository, analytics: AnalyticsService) -> None:
        super().__init__()
        self.repository = repository
        self.analytics = analytics

        self.setWindowTitle("Дневник-трекер дисгидротической экземы")
        self.resize(1200, 800)

        tabs = QTabWidget()
        self.daily_tab = DailyEntryTab(repository)
        self.history_tab = HistoryTab(repository, self._load_day)
        self.analytics_tab = AnalyticsTab(analytics)

        tabs.addTab(self.daily_tab, "Запись дня")
        tabs.addTab(self.history_tab, "История")
        tabs.addTab(self.analytics_tab, "Аналитика")

        tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(tabs)

    def _on_tab_changed(self, idx: int) -> None:
        if idx == 1:
            self.history_tab.refresh()
        if idx == 2:
            self.analytics_tab.refresh()

    def _load_day(self, entry_date: date) -> None:
        entry = self.repository.get_entry_by_date(entry_date)
        if entry:
            self.daily_tab.load_entry(entry)
