from __future__ import annotations

from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

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
        self.resize(1320, 860)

        container = QWidget()
        root = QHBoxLayout(container)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)

        title = QLabel("Экзема-трекер")
        title.setObjectName("title")
        title.setStyleSheet("color: #f8fafc;")
        subtitle = QLabel("Персональный офлайн-дневник")
        subtitle.setStyleSheet("color: #94a3b8;")

        self.menu = QListWidget()
        self.menu.setObjectName("menu")
        for item in ["Запись дня", "История", "Аналитика"]:
            QListWidgetItem(item, self.menu)
        self.menu.setCurrentRow(0)

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addWidget(self.menu)
        sidebar_layout.addStretch()

        self.stack = QStackedWidget()
        self.daily_tab = DailyEntryTab(repository)
        self.history_tab = HistoryTab(repository, self._load_day)
        self.analytics_tab = AnalyticsTab(analytics)

        self.stack.addWidget(self.daily_tab)
        self.stack.addWidget(self.history_tab)
        self.stack.addWidget(self.analytics_tab)

        self.menu.currentRowChanged.connect(self._on_page_changed)

        root.addWidget(sidebar, 1)
        root.addWidget(self.stack, 4)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        self.setCentralWidget(container)

    def _on_page_changed(self, idx: int) -> None:
        self.stack.setCurrentIndex(idx)
        if idx == 1:
            self.history_tab.refresh()
        elif idx == 2:
            self.analytics_tab.refresh()

    def _load_day(self, entry_date: date) -> None:
        entry = self.repository.get_entry_by_date(entry_date)
        if entry:
            self.daily_tab.load_entry(entry)
            self.menu.setCurrentRow(0)
