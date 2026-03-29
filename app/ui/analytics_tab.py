from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QLabel, QSplitter, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.services.analytics_service import AnalyticsService


class AnalyticsTab(QWidget):
    def __init__(self, analytics: AnalyticsService) -> None:
        super().__init__()
        self.analytics = analytics

        root = QVBoxLayout(self)
        self.summary = QLabel("Аналитика пока не рассчитана")
        self.summary.setWordWrap(True)

        splitter = QSplitter()

        left = QWidget()
        left_layout = QVBoxLayout(left)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["factor", "worsening %", "normal %", "score", "relation"])

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvasQTAgg(self.figure)

        left_layout.addWidget(self.table)
        left_layout.addWidget(self.canvas)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.web_view = QWebEngineView()
        right_layout.addWidget(self.web_view)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([700, 500])

        root.addWidget(self.summary)
        root.addWidget(splitter)

    def refresh(self) -> None:
        report = self.analytics.build_report()
        self.summary.setText(
            f"Записей: {report.total_entries}; ухудшений: {report.worsening_days}; обычных: {report.normal_days}.\n"
            + report.worsening_explanation
        )

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

        self.web_view.setHtml(self._build_html_report(report.worsening_explanation, report.improvement_explanation, top))

    def _build_html_report(self, worsening_text: str, improve_text: str, top) -> str:
        items = "".join(
            [f"<li><b>{x.factor}</b>: score={x.score:.3f}, связь: {x.relation}</li>" for x in top[:5]]
        ) or "<li>Недостаточно данных.</li>"
        return f"""
        <html>
            <body style='font-family:Segoe UI; padding:16px; background:#f8fafc; color:#0f172a;'>
                <h2 style='margin-bottom:6px;'>Понятное объяснение</h2>
                <div style='background:#ffffff; border:1px solid #dbe3ef; border-radius:12px; padding:12px; margin-bottom:12px;'>
                    <h3>Возможные причины ухудшения</h3>
                    <p>{worsening_text}</p>
                </div>
                <div style='background:#ffffff; border:1px solid #dbe3ef; border-radius:12px; padding:12px; margin-bottom:12px;'>
                    <h3>Что чаще совпадает с улучшением</h3>
                    <p>{improve_text}</p>
                </div>
                <div style='background:#ffffff; border:1px solid #dbe3ef; border-radius:12px; padding:12px;'>
                    <h3>Топ предполагаемых триггеров</h3>
                    <ul>{items}</ul>
                    <p style='color:#475569;'>Важно: это не диагноз, а наблюдения по совпадениям.</p>
                </div>
            </body>
        </html>
        """
