# Экзема-трекер (Web, офлайн)

Полностью русскоязычное **веб-приложение** на Python + Flask + SQLite для ежедневного ведения дневника дисгидротической экземы и поиска предполагаемых триггеров.

> Важно: приложение не ставит диагноз, а показывает только вероятные совпадения факторов.

## 1) Архитектура проекта

Используется слоистая архитектура:

- **UI Layer (Web UI)**: Jinja2 шаблоны + CSS + Bootstrap (`app/web/templates`, `app/web/static`).
- **Domain Logic**: модели `DailyEntry`, `TriggerScore`, `AnalyticsReport` (`app/domain/models.py`).
- **Data Layer**: SQLite и репозиторий (`app/data/database.py`, `app/data/repository.py`).
- **Services**: аналитика/расчёты (`app/services/analytics_service.py`).

Паттерн: **MVC для веба** (routes/controller + templates/view + repository/service/model).

## 2) Структура файлов

```text
app/
  main.py
  domain/models.py
  data/database.py
  data/repository.py
  services/analytics_service.py
  web/
    __init__.py
    routes.py
    templates/
      base.html
      dashboard.html
      entry_form.html
      history.html
      analytics.html
    static/
      style.css
run.py
requirements.txt
```

## 3) Схема базы данных

SQLite таблицы:

- `entries`
- `symptoms`
- `triggers_food`
- `triggers_contact`
- `custom_triggers`
- `photos`

## 4) UI (экраны)

- **Главная**: карточки со сводкой, быстрый вывод аналитики, последние записи.
- **Новая запись**: большая форма с секциями по ТЗ.
- **История**: таблица всех записей.
- **Аналитика**: текстовые объяснения, график Plotly, ranking-таблица факторов.

## 5) Реализация аналитики

Базовая логика:

- `score = frequency_in_worsening - frequency_in_normal`
- `> 0.4` высокая связь
- `0.2–0.4` средняя
- `0.1–0.2` слабая
- `< 0.1` явной связи нет

## 6) Код по модулям

- `app/web/routes.py`: маршруты, парсинг формы, подготовка данных для страниц.
- `app/services/analytics_service.py`: подсчёт частот/score, тексты объяснений.
- `app/data/repository.py`: сохранение, чтение, upsert по дате.

## 7) Инструкция запуска

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Откройте: `http://127.0.0.1:5000`

## 8) Сборка в .exe

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --name eczema_tracker_web run.py
```

Запуск exe поднимет локальный сервер Flask.
