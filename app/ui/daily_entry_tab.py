from __future__ import annotations

from datetime import date

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.data.repository import EntryRepository
from app.domain.models import DailyEntry


class DailyEntryTab(QWidget):
    FOOD_PRESETS = ["цитрусы", "острое", "сладкое", "молочное", "кофе"]
    CONTACT_PRESETS = ["бытовая химия", "перчатки", "мыло", "металл", "косметика"]
    GI_PRESETS = ["вздутие", "боль", "тошнота", "изжога", "неустойчивый стул"]
    LOCATION_PRESETS = ["ладони", "пальцы", "стопы", "запястья", "другое"]

    def __init__(self, repository: EntryRepository) -> None:
        super().__init__()
        self.repository = repository
        self.photo_paths: list[str] = []
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        self.entry_date = QDateEdit()
        self.entry_date.setCalendarPopup(True)
        self.entry_date.setDate(QDate.currentDate())

        skin_box = self._build_skin_group()
        stress_box = self._build_stress_group()
        env_box = self._build_environment_group()
        gi_box = self._build_gi_group()
        triggers_box = self._build_triggers_group()
        treatment_box = self._build_treatment_group()
        photos_box = self._build_photos_group()

        top_grid = QGridLayout()
        top_grid.addWidget(skin_box, 0, 0)
        top_grid.addWidget(stress_box, 0, 1)
        top_grid.addWidget(env_box, 1, 0)
        top_grid.addWidget(gi_box, 1, 1)
        top_grid.addWidget(triggers_box, 2, 0, 1, 2)
        top_grid.addWidget(treatment_box, 3, 0)
        top_grid.addWidget(photos_box, 3, 1)

        day_row = QHBoxLayout()
        day_row.addWidget(QLabel("Дата:"))
        day_row.addWidget(self.entry_date)
        day_row.addStretch()

        self.day_result = QComboBox()
        self.day_result.addItems(["worsening", "neutral", "improvement", "remission"])
        day_row.addWidget(QLabel("Итог дня:"))
        day_row.addWidget(self.day_result)

        save_btn = QPushButton("Сохранить запись")
        save_btn.clicked.connect(self.save_entry)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.addLayout(day_row)
        content_layout.addLayout(top_grid)
        content_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)

        root.addWidget(scroll)

    def _build_skin_group(self) -> QGroupBox:
        box = QGroupBox("Состояние кожи")
        form = QFormLayout(box)

        self.rash_present = QCheckBox("Есть сыпь")
        self.severity = self._slider()
        self.itch = self._slider()
        self.burning = self._slider()
        self.dryness = self._slider()
        self.location = self._multi_select(self.LOCATION_PRESETS)
        self.comment = QTextEdit()

        form.addRow(self.rash_present)
        form.addRow("Тяжесть (0-10)", self.severity)
        form.addRow("Зуд (0-10)", self.itch)
        form.addRow("Жжение (0-10)", self.burning)
        form.addRow("Сухость (0-10)", self.dryness)
        form.addRow("Локализация", self.location)
        form.addRow("Комментарий", self.comment)
        return box

    def _build_stress_group(self) -> QGroupBox:
        box = QGroupBox("Стресс и самочувствие")
        form = QFormLayout(box)
        self.stress_level = self._slider()
        self.strong_stress = QCheckBox("Сильный стресс")
        self.sleep_hours = QSlider(Qt.Orientation.Horizontal)
        self.sleep_hours.setRange(0, 12)
        self.sleep_hours.setValue(7)
        self.sleep_quality = self._slider()
        self.wellbeing = self._slider()

        form.addRow("Стресс (0-10)", self.stress_level)
        form.addRow(self.strong_stress)
        form.addRow("Сон (часов)", self.sleep_hours)
        form.addRow("Качество сна", self.sleep_quality)
        form.addRow("Самочувствие", self.wellbeing)
        return box

    def _build_environment_group(self) -> QGroupBox:
        box = QGroupBox("Потливость / среда")
        form = QFormLayout(box)
        self.sweating = self._slider()
        self.heat = QCheckBox("Жарко")
        self.wet_skin = QCheckBox("Влажная кожа")
        self.friction = QCheckBox("Трение")

        form.addRow("Потливость", self.sweating)
        form.addRow(self.heat)
        form.addRow(self.wet_skin)
        form.addRow(self.friction)
        return box

    def _build_gi_group(self) -> QGroupBox:
        box = QGroupBox("ЖКТ")
        form = QFormLayout(box)
        self.gi_issues = QCheckBox("Есть симптомы ЖКТ")
        self.gi_severity = self._slider()
        self.gi_symptoms = self._multi_select(self.GI_PRESETS)
        self.gi_comment = QTextEdit()

        form.addRow(self.gi_issues)
        form.addRow("Тяжесть", self.gi_severity)
        form.addRow("Симптомы", self.gi_symptoms)
        form.addRow("Комментарий", self.gi_comment)
        return box

    def _build_triggers_group(self) -> QGroupBox:
        box = QGroupBox("Пищевые и контактные триггеры")
        layout = QHBoxLayout(box)

        self.food_list = self._multi_select(self.FOOD_PRESETS)
        self.contact_list = self._multi_select(self.CONTACT_PRESETS)
        self.food_custom = QLineEdit()
        self.contact_custom = QLineEdit()

        left = QVBoxLayout()
        left.addWidget(QLabel("Пищевые"))
        left.addWidget(self.food_list)
        left.addWidget(QLabel("Кастомный пищевой (через запятую)"))
        left.addWidget(self.food_custom)

        right = QVBoxLayout()
        right.addWidget(QLabel("Контактные"))
        right.addWidget(self.contact_list)
        right.addWidget(QLabel("Кастомный контактный (через запятую)"))
        right.addWidget(self.contact_custom)

        layout.addLayout(left)
        layout.addLayout(right)
        return box

    def _build_treatment_group(self) -> QGroupBox:
        box = QGroupBox("Лечение")
        form = QFormLayout(box)
        self.moisturizer = QCheckBox("Увлажнение")
        self.medication = QCheckBox("Медикаменты")
        self.antihistamines = QCheckBox("Антигистаминные")
        self.steroids = QCheckBox("Стероиды")
        self.treatment_other = QLineEdit()

        form.addRow(self.moisturizer)
        form.addRow(self.medication)
        form.addRow(self.antihistamines)
        form.addRow(self.steroids)
        form.addRow("Другое", self.treatment_other)
        return box

    def _build_photos_group(self) -> QGroupBox:
        box = QGroupBox("Фото")
        layout = QVBoxLayout(box)
        self.photos_list = QListWidget()

        add_btn = QPushButton("Добавить фото")
        add_btn.clicked.connect(self._add_photos)

        layout.addWidget(self.photos_list)
        layout.addWidget(add_btn)
        return box

    def save_entry(self) -> None:
        entry = DailyEntry(
            id=None,
            entry_date=self.entry_date.date().toPyDate(),
            rash_present=self.rash_present.isChecked(),
            severity=self.severity.value(),
            itch=self.itch.value(),
            burning=self.burning.value(),
            dryness=self.dryness.value(),
            location=self._selected(self.location),
            comment=self.comment.toPlainText().strip(),
            stress_level=self.stress_level.value(),
            strong_stress=self.strong_stress.isChecked(),
            sleep_hours=self.sleep_hours.value(),
            sleep_quality=self.sleep_quality.value(),
            wellbeing=self.wellbeing.value(),
            sweating=self.sweating.value(),
            heat=self.heat.isChecked(),
            wet_skin=self.wet_skin.isChecked(),
            friction=self.friction.isChecked(),
            gi_issues=self.gi_issues.isChecked(),
            gi_severity=self.gi_severity.value(),
            gi_symptoms=self._selected(self.gi_symptoms),
            gi_comment=self.gi_comment.toPlainText().strip(),
            food_triggers=self._selected(self.food_list) + self._custom_values(self.food_custom),
            contact_triggers=self._selected(self.contact_list) + self._custom_values(self.contact_custom),
            moisturizer=self.moisturizer.isChecked(),
            medication=self.medication.isChecked(),
            antihistamines=self.antihistamines.isChecked(),
            steroids=self.steroids.isChecked(),
            treatment_other=self.treatment_other.text().strip(),
            photos=list(self.photo_paths),
            day_result=self.day_result.currentText(),
        )
        self.repository.upsert_entry(entry)
        QMessageBox.information(self, "Готово", "Запись сохранена.")

    def load_entry(self, entry: DailyEntry) -> None:
        self.entry_date.setDate(QDate(entry.entry_date.year, entry.entry_date.month, entry.entry_date.day))
        self.rash_present.setChecked(entry.rash_present)
        self.severity.setValue(entry.severity)
        self.itch.setValue(entry.itch)
        self.burning.setValue(entry.burning)
        self.dryness.setValue(entry.dryness)
        self._mark_selected(self.location, entry.location)
        self.comment.setPlainText(entry.comment)
        self.stress_level.setValue(entry.stress_level)
        self.strong_stress.setChecked(entry.strong_stress)
        self.sleep_hours.setValue(entry.sleep_hours)
        self.sleep_quality.setValue(entry.sleep_quality)
        self.wellbeing.setValue(entry.wellbeing)
        self.sweating.setValue(entry.sweating)
        self.heat.setChecked(entry.heat)
        self.wet_skin.setChecked(entry.wet_skin)
        self.friction.setChecked(entry.friction)
        self.gi_issues.setChecked(entry.gi_issues)
        self.gi_severity.setValue(entry.gi_severity)
        self._mark_selected(self.gi_symptoms, entry.gi_symptoms)
        self.gi_comment.setPlainText(entry.gi_comment)
        self._mark_selected(self.food_list, [t for t in entry.food_triggers if not t.startswith("custom:")])
        self._mark_selected(self.contact_list, [t for t in entry.contact_triggers if not t.startswith("custom:")])
        self.food_custom.setText(", ".join([t.replace("custom:", "") for t in entry.food_triggers if t.startswith("custom:")]))
        self.contact_custom.setText(", ".join([t.replace("custom:", "") for t in entry.contact_triggers if t.startswith("custom:")]))
        self.moisturizer.setChecked(entry.moisturizer)
        self.medication.setChecked(entry.medication)
        self.antihistamines.setChecked(entry.antihistamines)
        self.steroids.setChecked(entry.steroids)
        self.treatment_other.setText(entry.treatment_other)
        self.day_result.setCurrentText(entry.day_result)

        self.photo_paths = list(entry.photos)
        self.photos_list.clear()
        self.photos_list.addItems(self.photo_paths)

    def _slider(self) -> QSlider:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 10)
        slider.setValue(0)
        return slider

    def _multi_select(self, values: list[str]) -> QListWidget:
        widget = QListWidget()
        widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for value in values:
            item = QListWidgetItem(value)
            widget.addItem(item)
        return widget

    def _selected(self, widget: QListWidget) -> list[str]:
        return [item.text() for item in widget.selectedItems()]

    def _custom_values(self, line: QLineEdit) -> list[str]:
        raw = [x.strip() for x in line.text().split(",") if x.strip()]
        return [f"custom:{item}" for item in raw]

    def _mark_selected(self, widget: QListWidget, values: list[str]) -> None:
        desired = set(values)
        for i in range(widget.count()):
            item = widget.item(i)
            item.setSelected(item.text() in desired)

    def _add_photos(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите фото",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if not files:
            return
        self.photo_paths.extend(files)
        self.photos_list.clear()
        self.photos_list.addItems(self.photo_paths)
