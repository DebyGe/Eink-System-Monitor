# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project Overview

Single-file Flask web application that serves a real-time system performance
dashboard optimized for e-ink displays. Monitors CPU, GPU, Memory, Disk, and
Network on Windows and Linux. The entire backend is `app.py` (≈170 lines);
the frontend is a single Jinja2 template at `templates/index.html`.

## Project Structure

```
Eink-Info/
├── app.py               # Flask server + all metrics collection logic
├── requirements.txt     # Runtime dependencies (flask, psutil, GPUtil)
├── templates/
│   └── index.html       # E-ink optimized Jinja2 HTML template
└── README.md            # User-facing documentation
```

## Python Version

Python **3.10+** is required. The codebase uses built-in generic syntax
(`list[dict]`) which is not available in earlier versions. Development has
been done on CPython 3.12.

## Dependencies

Install with:

```bash
pip install -r requirements.txt
```

Runtime dependencies only:

| Package  | Purpose                         |
|----------|---------------------------------|
| flask    | Web server + Jinja2 templating  |
| psutil   | CPU, memory, disk, network data |
| GPUtil   | NVIDIA GPU data (optional)      |

There are no dev dependencies, no lock file, and no extras.

## Build / Run / Test Commands

### Run the server

```bash
python app.py
```

Starts Flask on `http://0.0.0.0:5000`.

### Quick smoke test (no test framework configured)

```bash
python -c "from app import collect_all; import json; print(json.dumps(collect_all(), indent=2))"
```

Verifies imports, data collection, and prints live metrics as JSON.

### Verify Flask routes load

```bash
python -c "from app import app; print([r.rule for r in app.url_map.iter_rules()])"
```

### No test framework

There are no tests, no `pytest`, no `unittest` files. If you add tests:

- Place them in a `tests/` directory.
- Use `pytest` as the runner.
- Run a single test: `pytest tests/test_file.py::test_name -v`
- Run all tests: `pytest tests/ -v`

### No linters or formatters configured

There is no ruff, black, isort, flake8, pylint, or mypy configuration. If
you add tooling, prefer `ruff` for both linting and formatting.

## Code Style Guidelines

Follow the conventions already established in `app.py`.

### Imports

- **Order**: stdlib → third-party → local, separated by blank lines (PEP 8).
- Use `from X import Y` when importing specific objects.
- Wrap optional/conditional imports in `try/except` with a boolean flag:

```python
try:
    import GPUtil
    GPU_AVAILABLE = True
except (ImportError, Exception):
    GPU_AVAILABLE = False
```

### Naming

| Element        | Convention           | Example                   |
|----------------|----------------------|---------------------------|
| Functions      | `snake_case`         | `get_cpu_info`            |
| Variables      | `snake_case`         | `uptime_seconds`          |
| Constants      | `UPPER_SNAKE_CASE`   | `GPU_AVAILABLE`           |
| Dict keys      | `snake_case` strings | `"usage_percent"`         |
| Route handlers | Short descriptive    | `index`, `api_stats`      |
| Flask app      | `app`                | `app = Flask(__name__)`   |

### Type Hints

- Add return type hints to all helper/data-collection functions.
- Use built-in generics (`list[dict]`, `dict[str, Any]`), not `typing`.
- Route handlers may omit return type hints.

```python
def get_cpu_info() -> dict:
    ...

def get_disk_info() -> list[dict]:
    ...
```

### Docstrings

- Use **PEP 257 one-liner** style with triple double-quotes.
- Every function must have a docstring.
- Module-level docstring at the top of each `.py` file.

```python
def get_memory_info() -> dict:
    """Return RAM and swap usage."""
```

### Formatting

- **4-space indentation** (no tabs).
- **Double quotes** for strings.
- Logical sections separated by comment banners:

```python
# ---------------------------------------------------------------------------
# Section Name
# ---------------------------------------------------------------------------
```

### Error Handling

- **Graceful degradation**: optional features (e.g., GPU) must work when the
  dependency is missing. Use a boolean flag pattern.
- **Catch specific exceptions**: prefer `except PermissionError` over bare
  `except Exception`.
- **Never crash the server**: wrap metric collection in try/except so one
  failing subsystem does not bring down the whole dashboard.
- **No logging module is used currently**. If you add error handling that
  needs visibility, use Python's `logging` module.

### HTML / CSS (templates/)

- **E-ink first**: black and white only, no colors, no gradients, no
  animations, no JavaScript unless absolutely necessary.
- **Monospace font**: `Courier New, Courier, monospace`.
- **CSS-only UI**: bar charts use `<span>` with `display: block` and
  percentage `width`, not `<canvas>` or JS libraries.
- All fill elements (`bar-fill`, `core-fill`) must have `display: block`.
- Auto-refresh via `<meta http-equiv="refresh" content="30">`.

### API Conventions

- Dashboard HTML: `GET /`
- JSON API: `GET /api/stats`
- All JSON keys use `snake_case`.
- Units are embedded in key names: `_gb`, `_mb`, `_mhz`, `_percent`, `_c`.

## Configuration

There is no config file. Settings are hardcoded in `app.py`:

| Setting        | Location                                | Default         |
|----------------|-----------------------------------------|-----------------|
| Port           | `app.run(port=5000)`                    | `5000`          |
| Host           | `app.run(host="0.0.0.0")`              | `0.0.0.0`       |
| Debug          | `app.run(debug=False)`                  | `False`         |
| Refresh rate   | `templates/index.html` meta tag         | `30` seconds    |

## Notes

- This is **not** a git repository. No `.gitignore` exists.
- No CI/CD, no Cursor rules, no Copilot instructions are present.
- No packaging metadata (`pyproject.toml`, `setup.py`) exists.
- The entire app is a single Python file — keep it simple.
