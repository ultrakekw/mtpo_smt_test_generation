# SMT-based test generation for Python benchmarks

Проект представляет собой исследовательский стенд для сравнения SMT-основанных методов генерации тестовых входов для Python-функций. В стенде сравниваются три подхода:

- `PyExZ3` - внешний concolic-инструмент из `deps/PyExZ3`;
- `CrossHair` - symbolic/SMT-инструмент, запускаемый через CLI `crosshair cover`;
- `mini` - собственный минимальный concolic-прототип на базе Z3.

Основная идея проекта - отделить генерацию входов от измерения покрытия. Каждый инструмент строит свои concrete-входы, после чего эти входы заново исполняются на общем `collect_branches`-счетчике. Благодаря этому покрытие считается одинаково для всех инструментов.

## Структура проекта

```text
.
├── benchmarks/        # benchmark-функции и общий каталог
├── tools/             # запуск экспериментов, concolic-прототип, генераторы материалов
├── tests/             # pytest-проверки проекта
├── results/           # JSON-результаты экспериментов
└──  deps/              # внешние инструменты и их исходный код
```

Ключевые файлы:

- `benchmarks/catalog.py` - единый каталог активных benchmark-функций, параметров и числа ветвей.
- `tools/run_suite.py` - запуск одного инструмента на выбранном наборе benchmark-функций.
- `tools/compare_algorithms.py` - сравнение `PyExZ3`, `CrossHair` и `mini` в одном запуске.
- `tools/run_extended_experiments.py` - серия запусков по `micro` и `industrial` suite.
- `tools/miniconcolic.py` - собственный concolic-прототип.
- `tests/test_extended_miniconcolic.py` - основные тесты корректности.

## Benchmark-suite

Активный набор задается в `benchmarks/catalog.py`.

Micro-suite:

- `threshold` - линейная цепочка условий;
- `pair_relation` - вложенные ветви и ограничения над двумя числами;
- `loop_bucket` - ограниченный цикл и постусловия после итераций.

Industrial-suite:

- `fastapi_status_body` - логика HTTP status code из FastAPI;
- `flask_load_dotenv` - интерпретация флага окружения из Flask;
- `pip_archive_suffix` - распознавание архивных суффиксов из pip;
- `werkzeug_server_name` - обработка схемы и стандартного порта из Werkzeug;
- `black_numeric_string` - классификация числовой строки из Black.

Каждый benchmark-файл содержит основную функцию и функцию `collect_branches`, которая возвращает множество покрытых ветвей для конкретного входа.

## Установка

Рекомендуется использовать Python 3.9+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install z3-solver crosshair-tool pytest python-docx python-pptx
```

Для полного сравнения нужен каталог `deps/PyExZ3`, так как `tools/run_suite.py` подключает его как локальную зависимость.

Важно: адаптер CrossHair сейчас вызывает CLI по пути `.venv/bin/crosshair`. Поэтому для запуска CrossHair нужно либо использовать виртуальное окружение `.venv`, либо поправить путь в `tools/run_suite.py`.

## Быстрый старт

Проверить тесты проекта:

```bash
python -m pytest -q tests
```

Запустить собственный concolic-прототип на всех benchmark-функциях:

```bash
python tools/run_suite.py --tool mini --suite all --max-iterations 20
```

Запустить PyExZ3 на industrial-suite:

```bash
python tools/run_suite.py --tool pyexz3 --suite industrial --max-iterations 20
```

Запустить CrossHair на micro-suite:

```bash
python tools/run_suite.py --tool crosshair --suite micro --max-iterations 20
```

## Сравнение инструментов

Сравнить все три инструмента и сохранить JSON:

```bash
python tools/compare_algorithms.py \
  --suite all \
  --runs 1 \
  --max-iterations 20 \
  --output results/algorithm_comparison.json
```

Запустить расширенную серию экспериментов:

```bash
python tools/run_extended_experiments.py --runs 5 --max-iterations 20
```

После расширенного запуска появляются файлы:

- `results/micro_*_run_*.json`;
- `results/industrial_*_run_*.json`;
- `results/micro_summary.json`;
- `results/industrial_summary.json`;
- `results/extended_summary.json`.

## Как работает стенд

1. `benchmarks/catalog.py` описывает функции, параметры, начальные значения, ограничения домена и число ветвей.
2. `tools/run_suite.py` выбирает benchmark-функции по `--suite`.
3. Адаптер выбранного инструмента генерирует concrete-входы.
4. Входы нормализуются к типам из `ParameterSpec`.
5. Для каждого входа вызывается `collect_branches`.
6. Покрытые ветви объединяются в одно множество.
7. Runner считает время, Python heap, Peak RSS, число уникальных тестов и процент покрытия.
8. Результат печатается как JSON.

Схема потока данных:

```text
benchmark catalog
      |
      v
tool adapter: PyExZ3 / CrossHair / mini
      |
      v
generated concrete inputs
      |
      v
common branch collector
      |
      v
metrics and JSON results
```

## Собственный concolic-прототип

`tools/miniconcolic.py` реализует небольшой concolic-движок:

- `SymInt`, `SymBool`, `SymStr` хранят concrete-значение и соответствующее Z3-выражение;
- `ExecutionTrace` записывает условия, встреченные при выполнении;
- `run_once` запускает benchmark-функцию на symbolic-обертках;
- `solve_path` инвертирует одно условие пути и решает новую формулу через Z3;
- `explore` обходит очередь найденных входов до лимита `max_iterations`.

Для строк задаются bounded-ограничения: максимальная длина и допустимый алфавит. Это делает поиск конечным и воспроизводимым.


## Проверка качества

Минимальная проверка перед публикацией:

```bash
python -m pytest -q tests
python tools/run_suite.py --tool mini --suite all --max-iterations 20
python tools/compare_algorithms.py --suite all --runs 1 --max-iterations 20
```

Ожидается, что тесты проходят, а команды запуска возвращают JSON без ошибок.

## Примечания

- Внешние проекты в `deps/` сохраняют собственную структуру и лицензии.
- `results/`, `reports/`, `presentations/` и `submissions/` являются артефактами экспериментов и оформления.