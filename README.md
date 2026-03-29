# Экзема-трекер (MVP)

Оффлайн десктоп-приложение на Python + PySide6 + SQLite для ежедневного ведения дневника и поиска предполагаемых триггеров дисгидротической экземы.

## Архитектура

Выбрана **MVVM-подобная** схема (для PySide6 это практично):

- **UI Layer (`app/ui`)**: формы, вкладки, таблицы, график.
- **Domain (`app/domain`)**: dataclass-модели `DailyEntry`, `TriggerScore`, `AnalyticsReport`.
- **Data Layer (`app/data`)**: SQLite схема + репозиторий CRUD.
- **Services (`app/services`)**: аналитика, подсчёты, текстовые объяснения.

Почему не чистый MVC: в Qt удобнее держать состояние формы в виджете, а вычисления выносить в сервисы/репозитории.

## Структура проекта

```text
app/
  main.py
  domain/models.py
  data/database.py
  data/repository.py
  services/analytics_service.py
  ui/main_window.py
  ui/daily_entry_tab.py
  ui/history_tab.py
  ui/analytics_tab.py
run.py
requirements.txt
```

## База данных

Таблицы:
- `entries` — основная запись дня
- `symptoms` — расширяемая таблица симптомов
- `triggers_food` — пищевые триггеры
- `triggers_contact` — контактные триггеры
- `custom_triggers` — словарь пользовательских триггеров
- `photos` — привязка фото к записи

## MVP-функциональность

- Ввод ежедневной записи (все блоки из ТЗ).
- Сохранение/обновление записи по дате.
- История записей с быстрым открытием.
- Аналитика:
  - `score = worsening_frequency - normal_frequency`
  - классификация силы связи
  - текст «возможных причин ухудшения»
  - факторы, чаще встречающиеся в улучшениях
  - график score по топ-факторам

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Сборка в exe

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name eczema_tracker run.py
```

Готовый exe появится в `dist/eczema_tracker.exe`.

## Ограничения MVP

- Фильтрация истории пока базовая.
- Нет отдельного мастера миграций БД.
- Нет импорта/экспорта (можно добавить на 2 этапе).
