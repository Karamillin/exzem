from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.services.analytics_service import AnalyticsService


class AnalyticsTab(QWidget):
    def __init__(self, analytics: AnalyticsService) -> None:
        super().__init__()
        self.analytics = analytics

        root = QVBoxLayout(self)
        self.summary = QLabel("Аналитика пока не рассчитана")
        self.summary.setWordWrap(True)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["factor", "worsening %", "normal %", "score", "relation"])

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.improve_label = QLabel("")
        self.improve_label.setWordWrap(True)

        root.addWidget(self.summary)
        root.addWidget(self.table)
        root.addWidget(self.canvas)
        root.addWidget(self.improve_label)

    def refresh(self) -> None:
        report = self.analytics.build_report()
        self.summary.setText(
            f"Записей: {report.total_entries}; ухудшений: {report.worsening_days}; обычных: {report.normal_days}.\n"
            + report.worsening_explanation
        )
        self.improve_label.setText(report.improvement_explanation)

        self.table.setRowCount(len(report.trigger_scores))
        for row, score in enumerate(report.trigger_scores):
            self.table.setItem(row, 0, QTableWidgetItem(score.factor))
            self.table.setItem(row, 1, QTableWidgetItem(f"{score.worsening_frequency * 100:.1f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{score.normal_frequency * 100:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{score.score:.3f}"))
            self.table.setItem(row, 4, QTableWidgetItem(score.relation))

        top = [x for x in report.trigger_scores if x.score > 0][:7]
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if top:
            names = [x.factor for x in top]
            values = [x.score for x in top]
            ax.barh(names, values)
            ax.set_title("Предполагаемые триггеры (score)")
            ax.set_xlabel("Частота в ухудшениях - частота в обычных днях")
        else:
            ax.text(0.1, 0.5, "Недостаточно данных для графика")
        self.figure.tight_layout()
        self.canvas.draw_idle()
