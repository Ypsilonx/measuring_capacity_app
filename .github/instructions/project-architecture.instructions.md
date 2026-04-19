---
description: "Use when adding new features, files, modules, or making structural changes to the measuring_capacity_app project. Enforces folder structure, naming conventions, import rules, and separation of concerns."
applyTo: "src/**"
---
# Architektura projektu — measuring_capacity_app

## Struktura složek — co kam patří

```
src/
  main.py          # POUZE spouštěcí orchestrace (init DB, dialog uživatele, launch okno)
  core/            # Byznys logika bez závislosti na GUI ani DB (výpočty, validace)
  database/        # POUZE databázová vrstva (models, crud, database)
  gui/             # POUZE GUI komponenty (okna, dialogy, panely)
  utils/           # Pomocné funkce sdílené napříč vrstvami (parsování, formátování)
scripts/           # Jednoúčelové skripty (seed, migrace, testování DB bez GUI)
tests/             # Testy odpovídají struktuře src/ (test_crud.py, test_models.py…)
data/              # Pouze datové soubory (SQLite DB, exporty)
```

**Nikdy nevkládej:**
- SQL dotazy nebo `db.query()` volání do GUI souborů
- Tvorbu widgetů nebo volání `ctk.*` do `database/` nebo `core/`
- Byznys logiku přímo do `main.py` — main.py jen orchestruje spuštění

## Pravidla pojmenování

| Co | Konvence | Příklad |
|----|----------|---------|
| Třídy | PascalCase | `PlannerWindow`, `TimeSession` |
| Funkce / metody | snake_case | `get_users()`, `start_tracking()` |
| Privátní metody | `_` prefix | `_create_widgets()`, `_on_start()` |
| GUI callbacky | `_on_<akce>` | `_on_start()`, `_on_pause()` |
| Enum třídy | PascalCase | `ActivityType`, `RoutineType` |
| Enum hodnoty | UPPER_CASE | `ACTIVE`, `PROJECT_TASK` |
| Soubory | snake_case | `tracking_dialog.py`, `new_project_task_dialog.py` |

## Jedno soubor = jedna odpovědnost

- Každý dialog/okno má vlastní soubor v `gui/`
- Každá skupina CRUD operací zůstává v `crud.py` — nerozděluj do více souborů, dokud `crud.py` nepřekročí ~600 řádků
- Nové modely patří do `models.py`, ne do nového souboru

## Importy — pořadí

```python
# 1. Standardní knihovna
import os
import sys

# 2. Externí balíčky
import customtkinter as ctk
from sqlalchemy.orm import Session

# 3. Interní moduly (relativní z src/)
from src.database import crud
from src.database.models import ActivityType
```

- Vždy používej relativní importy z `src/` (ne absolutní systémové cesty)
- `sys.path.insert()` patří výhradně do `main.py`

## Nový soubor — checklist

Před vytvořením nového souboru v `src/`:
1. Patří kód do existujícího souboru? (do 300–400 řádků)
2. Je to GUI komponenta? → `src/gui/<název_dialogu>.py`
3. Je to databázová operace? → přidej funkci do `src/database/crud.py`
4. Je to sdílená pomocná funkce? → `src/utils/<téma>.py`
5. Je to byznys logika bez GUI/DB závislostí? → `src/core/<téma>.py`
