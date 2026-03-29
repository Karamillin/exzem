from __future__ import annotations

from datetime import date
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.data.repository import EntryRepository


class HistoryTab(QWidget):
    def __init__(self, repository: EntryRepository, on_open: Callable[[date], None]) -> None:
        super().__init__()
        self.repository = repository
        self.on_open = on_open

        root = QVBoxLayout(self)
        self.items = QListWidget()
        self.items.itemDoubleClicked.connect(self._open_item)

        row = QHBoxLayout()
        self.count_label = QLabel("Записей: 0")
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.refresh)

        row.addWidget(self.count_label)
        row.addStretch()
        row.addWidget(refresh_btn)

        tip = QLabel("Подсказка: двойной клик по строке откроет запись в форме редактирования.")
        tip.setStyleSheet("color: #475569;")

        root.addWidget(tip)
        root.addLayout(row)
        root.addWidget(self.items)

    def refresh(self) -> None:
        entries = self.repository.list_entries()
        self.items.clear()
        for entry in entries:
            item = QListWidgetItem(
                f"{entry.entry_date.isoformat()} | {entry.day_result} | стресс {entry.stress_level} | зуд {entry.itch}"
            )
            item.setData(Qt.ItemDataRole.UserRole, entry.entry_date.isoformat())
            self.items.addItem(item)
        self.count_label.setText(f"Записей: {len(entries)}")

    def _open_item(self, item: QListWidgetItem) -> None:
        selected = date.fromisoformat(item.data(Qt.ItemDataRole.UserRole))
        self.on_open(selected)
