# 📊 STAV PROJEKTU — measuring_capacity_app

> Naposledy aktualizováno: 27.4.2026

---

## 📌 KDE JSME TEĎ

**MVP je funkční.** Aplikace zvládá celý základní workflow od vytvoření úkolu přes tracking s fázemi až po sumarizaci. Databázová vrstva je stabilní. GUI je responzivní a multi-user.

Nově (duben 2026):
- Přidány instrukce pro AI asistenta (`.github/instructions/`) — konvence architektury, DB vrstvy a GUI vrstvy
- Implementován centrální logger (`src/utils/app_logger.py`) — zápis do `data/app.log` (rotující), konzole a GUI
- Přidán `LogPanel` widget do spodní části `PlannerWindow` — live přehled akcí (4 řádky, read-only)
- Veškerý `print()` nahrazen `logger.info/warning/error()` ve všech src souborech
- Formulářová validace v `NewProjectTaskDialog` — prázdná pole, duplicitní TMA (ACTIVE = blokace, COMPLETED = panel pro znovuotevření)
- `ConfirmDialog` — znovupoužitelný modální dialog pro potvrzení destruktivních akcí
- Toolbar v `PlannerWindow` — datum, jméno uživatele, tlačítko „Přepnout uživatele" bez restartu aplikace
- Pytest testy pro `crud.py` — 16 testů, in-memory SQLite, 0 failures

Nově (27.4.2026):
- Implementovány P2 funkce (editace dat):
  - `crud.delete_time_session()` — smazání konkrétní session
  - `crud.delete_activity()` — smazání aktivity + cascade sessions
  - `crud.update_time_session_notes()` — editace poznámek session
  - `crud.update_activity()` — editace metadat PROJECT_TASK
  - `EditActivityDialog` (nový soubor) — předvyplněný formulář pro editaci aktivity
  - `InputDialog` rozšířen o parametr `initial_value` (předvyplnění) a opraven prázdný výsledek pro `required=False`
  - `TaskCard` v `PlannerWindow` — přidána tlačítka ✏️ Editovat + 🗑️ Smazat pro aktivitu
  - `TaskCard` sessions seznam — přidána tlačítka ✏️ (editace poznámek) + 🗑️ (smazání) u každé session
- Pytest testy rozšířeny na 26 (přidáno 10 testů pro P2 funkce), 0 failures
- `TaskCard` zobrazuje autora aktivity (`👤 Jméno`) přímo v záhlaví karty
- Každá session v rozbalovacím seznamu ukazuje kdo ji trackoval (`👤 Jméno`)
- Pravý panel v `PlannerWindow` má novou sekci „📋 Dnes zadáno" — live přehled dnešních rutin (typ, délka, čas, kdo zadal); obnovuje se po každé rutině i po zavření TrackingDialog
- Opraveno řazení „Poslední fáze" v `TaskCard` — nyní vždy správně ukazuje časově nejnovější validní session (fix: `max(..., key=lambda s: s.start_time)`)
- Opravena chyba `invalid command name` při startu — pending Tkinter `after()` callbacky se před `root.destroy()` explicitně ruší
- Přidána `make_ctk_error_handler()` v `app_logger.py` — Tkinter error handler potlačující CTk interní šum, nasazen na `PlannerWindow.root`

**Aktuální zaměření:** P2 editace hotová. Zbývají P3 (statistiky) a P4 (pokročilé).

---

## ✅ CO JE HOTOVO

### **1. Databázová vrstva** (100%)
- ✅ SQLAlchemy ORM modely
- ✅ SQLite databáze
- ✅ CRUD operace pro všechny entity
- ✅ Podpora pro:
  - PROJECT_TASK aktivity s ENUM ObsahMereniType
  - ROUTINE aktivity s ENUM RoutineType (9 typů)
  - Fázové měření (Příprava/Měření/Úklid)
  - Více TimeSession na aktivitu
  - Validace session (`is_valid` flag) s důvodem invalidace
  - Číselníky (Zadavatelé, Projekty, Důvody)
  - Multi-user podpora
  - Oddělené Zadavatel a Projekt entity
- ✅ `get_today_routines(db)` — vrací dnešní ROUTINE aktivity seřazené od nejnovější

**Soubory:**
- [src/database/models.py](src/database/models.py) - DB modely s ENUMs
- [src/database/database.py](src/database/database.py) - Engine & session
- [src/database/crud.py](src/database/crud.py) - CRUD operace

### **2. GUI vrstva** (MVP kompletní + vylepšení)
- ✅ CustomTkinter desktop aplikace (dark mode)
- ✅ UserSelectionDialog - výběr uživatele při startu
- ✅ PlannerWindow - hlavní okno se 2 panely:
  - PROJECT_TASKS panel (80% šířky) s TaskCard widgety
  - ROUTINES panel (20% šířky) s 9 quick-action tlačítky + sekce „📋 Dnes zadáno"
- ✅ TaskCard s rámečky a rozbalovacím seznamem sessions:
  - Zobrazení validních i invalidních sessions
  - Ikony ✅/❌ podle validity
  - Důvod invalidace v závorce
  - Poslední fáze v souhrnu (dle `start_time` — vždy časově nejnovější)
  - Autor aktivity (`👤 Jméno`) v záhlaví karty
  - Kdo trackoval (`👤 Jméno`) u každé session v rozbalovacím seznamu
- ✅ TrackingDialog - široké okno se 2 sloupci:
  - Levý sloupec: info, fáze, časovač, ovládání
  - Pravý sloupec: ROUTINES buttons (9 typů)
  - PAUZA s elapsed time tracking (čas skutečně stojí)
  - STOP-OK/STOP-NOK s InputDialog pro důvod
- ✅ RoutineDialog - vytvoření ROUTINE s editací času
- ✅ NewProjectTaskDialog - formulář pro nový PROJECT_TASK
- ✅ InputDialog - jednoduchý vstup textu
- ✅ Responzivní design pro různá rozlišení (notebooky i velké monitory)
- ✅ LogPanel - read-only log panel ve spodní části PlannerWindow (4 řádky, auto-scroll)

**Soubory:**
- [src/gui/planner_window.py](src/gui/planner_window.py)
- [src/gui/user_selection_dialog.py](src/gui/user_selection_dialog.py)
- [src/gui/tracking_dialog.py](src/gui/tracking_dialog.py)
- [src/gui/routine_dialog.py](src/gui/routine_dialog.py)
- [src/gui/new_project_task_dialog.py](src/gui/new_project_task_dialog.py)
- [src/gui/confirm_dialog.py](src/gui/confirm_dialog.py)
- [src/gui/input_dialog.py](src/gui/input_dialog.py)
- [src/gui/log_panel.py](src/gui/log_panel.py)

### **3. Pomocné scripty**
- ✅ [scripts/test_database.py](scripts/test_database.py) - Test DB bez GUI
- ✅ [scripts/seed_database.py](scripts/seed_database.py) - Naplnění testovacími daty

### **4. Infrastruktura — Logging, dialogy, testy**
- ✅ `src/utils/app_logger.py` — singleton `get_logger()`, RotatingFileHandler, GUI dispatch
- ✅ `make_ctk_error_handler()` — Tkinter error handler potlačující CTk interní after() šum; nasazen na `PlannerWindow.root`
- ✅ `data/app.log` — rotující log soubor (max 1 MB, 3 zálohy)
- ✅ `src/gui/confirm_dialog.py` — znovupoužitelný `ConfirmDialog` (title, message, tlačítka, barvy)
- ✅ `src/gui/log_panel.py` — `LogPanel` widget ve spodní části `PlannerWindow`
- ✅ `src/gui/edit_activity_dialog.py` — `EditActivityDialog` — editace metadat PROJECT_TASK (předvyplněný formulář)
- ✅ `tests/test_crud.py` — 26 pytest testů (User, Activity, TimeSession, P2 delete/update), 0 failures
- ✅ Fix: pending `after()` callbacky se ruší před `root.destroy()` v `main.py` — eliminace `invalid command name` Tkinter chyb při startu

### **5. Dokumentace & konvence**
- ✅ [README.md](README.md) — přehled projektu, schéma DB, workflow
- ✅ [QUICKSTART.md](QUICKSTART.md) — jak spustit, seed, ovládání
- ✅ [PROJECT_CONFIG.md](PROJECT_CONFIG.md) — dev pravidla, příkazy
- ✅ [.github/instructions/project-architecture.instructions.md](.github/instructions/project-architecture.instructions.md) — struktura složek, pojmenování, importy
- ✅ [.github/instructions/database-layer.instructions.md](.github/instructions/database-layer.instructions.md) — SQLAlchemy vzory, CRUD konvence, session management
- ✅ [.github/instructions/gui-layer.instructions.md](.github/instructions/gui-layer.instructions.md) — CustomTkinter konvence, dialog komunikace, timer pravidla

---

## 🎯 PODPOROVANÝ WORKFLOW

### **Reálný use case:**
1. **Ráno:** Vytvoř PROJECT_TASK pro dnešní měření
2. **Start práce:** Vyber fázi "Příprava" → START
3. **Během dne:**
   - Přerušení → STOP
   - Pokračování → START (ve stejné fázi)
   - Přechod na "Měření" → START v nové fázi
   - Opakované session v jedné fázi (pokud je potřeba)
4. **Večer:**
   - Pokud je úkol hotový → Dokončit
   - Pokud ne → nechá se ACTIVE (zobrazí se další den)
5. **Další den:** Úkol je stále v seznamu → pokračuj

### **Funguje:**
- ✅ Multi-user - výběr uživatele při startu
- ✅ Přepínání uživatele za běhu (toolbar tlačítko, bez restartu aplikace)
- ✅ Jeden úkol = mnoho session (i ve stejné fázi)
- ✅ PAUZA s možností zaznamenání ROUTINE
- ✅ Změna fází kdykoliv
- ✅ Živý časovač s real-time zobrazením (při PAUZA skutečně stojí)
- ✅ Sumarizace validního času
- ✅ Zobrazení validních i invalidních sessions v rozbalovacím seznamu
- ✅ STOP-NOK s důvodem invalidace
- ✅ 9 typů ROUTINE aktivit s přednastavenými časy
- ✅ Responzivní design pro různá rozlišení
- ✅ Aktivní úkoly zůstávají v seznamu

---

## 🗂️ TODO — Backlog (seřazeno dle priority)

### 🔴 Priorita 1 — Opravy a stabilita (udělat jako první)

| # | Úkol | Popis |
|---|------|-------|
| ~~P1-1~~ | ~~Error handling formulářů~~ | ✅ Hotovo — validace vstupů, duplicitní TMA (reopen panel pro COMPLETED) |
| ~~P1-2~~ | ~~Potvrzovací dialogy~~ | ✅ Hotovo — `ConfirmDialog` + potvrzení před dokončením úkolu |
| ~~P1-3~~ | ~~Logging~~ | ✅ Hotovo — `src/utils/app_logger.py` + `LogPanel` v GUI + `data/app.log` |
| ~~P1-4~~ | ~~Základní testy~~ | ✅ Hotovo — `tests/test_crud.py`, 16 testů, 0 failures |

### 🟡 Priorita 2 — Editace dat (uživatelský komfort)

| # | Úkol | Popis |
|---|------|-------|
| ~~P2-1~~ | ~~Editace aktivity~~ | ✅ Hotovo — `EditActivityDialog` + `crud.update_activity()` |
| ~~P2-2~~ | ~~Editace poznámek session~~ | ✅ Hotovo — `InputDialog` s `initial_value` + `crud.update_time_session_notes()` |
| ~~P2-3~~ | ~~Mazání session~~ | ✅ Hotovo — `crud.delete_time_session()` + tlačítko 🗑️ v TaskCard sessions |
| ~~P2-4~~ | ~~Mazání aktivity~~ | ✅ Hotovo — `crud.delete_activity()` (cascade) + tlačítko 🗑️ Smazat v TaskCard |

### 🟢 Priorita 3 — Statistiky a analytika (hlavní přidaná hodnota)

| # | Úkol | Popis |
|---|------|-------|
| P3-1 | Statistiky úkolu | Průměrná délka session, celkový čas po fázích, počet přerušení |
| P3-2 | Denní přehled | Kolik hodin odpracováno dnes (PROJECT_TASK + ROUTINE breakdown) |
| P3-3 | Týdenní přehled | Agregovaný přehled po dnech, graf |
| P3-4 | Fázový breakdown | Graf: kolik % času Příprava / Měření / Úklid pro daný úkol |
| P3-5 | Predikce | Odhad zbývajícího času na základě historických dat stejného typu |
| P3-6 | Export dat | Export do CSV/Excel (Pandas) |
| P3-7 | Filtr přehledů per-user | Statistiky a přehledy filtrovatelné podle profilu (uživatele). Datový model to již podporuje: `Activity.created_by_id` = kdo úkol zadal, `TimeSession.user_id` = kdo trackoval čas. V `crud.get_activities()` přidat volitelný parametr `created_by_id`. Sdílený seznam úkolů zůstává — filtr se týká jen přehledů/statistik. |

### 🔵 Priorita 4 — Pokročilé funkce (nice to have)

| # | Úkol | Popis |
|---|------|-------|
| P4-1 | Filtrování aktivit | Filtr v PlannerWindow dle zadavatele / projektu / data |
| P4-2 | Vyhledávání | Fulltextové hledání v TMA a názvech testů |
| P4-3 | Archiv dokončených | Okno/tab pro prohlížení COMPLETED aktivit |
| P4-4 | PostgreSQL migrace | Volitelný přechod z SQLite na PostgreSQL (Alembic migrace) |
| P4-5 | Notifikace | Upozornění při dlouhé pauze nebo dosažení odhadovaného času |

---

## 📈 STATISTIKY KÓDU (duben 2026)

```
Celkem řádků:   ~2600 LOC
Python soubory: 14 souborů src/ + 2 skripty + 1 test
GUI komponenty: 11 souborů (gui/) — nově edit_activity_dialog.py
DB operace:     ~29 CRUD funkcí (nové: delete_session, delete_activity, update_notes, update_activity)
Tabulky DB:     8 (users, activities, time_sessions + 5 číselníků)
Instrukce AI:   3 soubory .github/instructions/
Pytest testy:   26 (tests/test_crud.py) — nově 10 P2 testů
```

---

## 🚀 JAK SPUSTIT

### **Quick Start:**
```powershell
# 1. Aktivuj venv
.\venv\Scripts\Activate.ps1

# 2. (Volitelné) Naplň testovacími daty
python scripts/seed_database.py

# 3. Spusť aplikaci
python src/main.py
```

### **Test bez GUI:**
```powershell
python scripts/test_database.py
```

---

## 🎨 ARCHITEKTURA

```
measuring_capacity_app/
│
├── src/
│   ├── main.py                         # Vstupní bod ✅
│   │
│   ├── database/                       # Databázová vrstva ✅
│   │   ├── models.py                   # SQLAlchemy modely + ENUMs
│   │   ├── database.py                 # Engine & SessionLocal
│   │   └── crud.py                     # ~25 CRUD funkcí
│   │
│   ├── gui/                            # GUI vrstva ✅
│   │   ├── planner_window.py           # Hlavní okno + toolbar
│   │   ├── user_selection_dialog.py    # Výběr / vytvoření uživatele
│   │   ├── tracking_dialog.py          # Tracking s fázemi + PAUZA
│   │   ├── routine_dialog.py           # Vytvoření ROUTINE
│   │   ├── new_project_task_dialog.py  # Formulář nového PROJECT_TASK
│   │   ├── confirm_dialog.py           # Znovupoužitelný ConfirmDialog
│   │   ├── input_dialog.py             # Jednoduchý vstup textu
│   │   ├── log_panel.py                # Read-only log panel (spodní lišta)
│   │   ├── activity_list.py            # (legacy, nepoužíváno aktivně)
│   │   ├── main_window.py              # (legacy, nepoužíváno aktivně)
│   │   ├── tracking_panel.py           # (legacy, nepoužíváno aktivně)
│   │   └── tracking_dialog_old.py      # (legacy, archiv)
│   │
│   ├── utils/                          # Pomocné funkce ✅
│   │   └── app_logger.py               # Singleton logger + GUI dispatch
│   │
│   └── core/                           # Business logika (prázdné, pro budoucí use)
│
├── tests/                              # Pytest testy ✅
│   └── test_crud.py                    # 16 testů, in-memory SQLite
│
├── scripts/                            # Pomocné scripty ✅
│   ├── test_database.py
│   └── seed_database.py
│
├── data/                               # Runtime data (není v gitu)
│   ├── measuring_capacity.db           # SQLite databáze
│   └── app.log                         # Rotující log (max 1 MB)
│
├── .github/instructions/               # Instrukce pro AI asistenta ✅
│   ├── project-architecture.instructions.md
│   ├── database-layer.instructions.md
│   └── gui-layer.instructions.md
│
├── venv/                               # Virtual environment
├── requirements.txt
├── README.md
├── QUICKSTART.md
├── MVP_STATUS.md
└── PROJECT_CONFIG.md
```

---

## 🔧 TECHNOLOGIE

### **Backend:**
- Python 3.13
- SQLAlchemy 2.0 (ORM)
- SQLite (databáze)

### **Frontend:**
- CustomTkinter 5.2 (GUI)
- Dark mode theme

### **Dev tools:**
- pytest 9.0 (testy — `tests/test_crud.py`, 16 testů)
- black (formatting — zatím neimplementováno)

---

## 💾 DATABÁZOVÉ SCHÉMA

### **Hlavní tabulky:**

**activities** (úkoly)
- `type`: ROUTINE / PROJECT_TASK
- `status`: ACTIVE / COMPLETED
- Pro PROJECT_TASK: TMA, název testu, projekt, zadavatel...

**time_sessions** (časové záznamy)
- `activity_id` → activities
- `start_time`, `end_time`, `duration_minutes`
- `phase`: Příprava / Měření / Úklid
- `is_valid`: TRUE/FALSE (pro validaci)
- `invalidation_reason`: důvod proč je neplatný

**users** (uživatelé)
- Multi-user podpora — výběr profilu při startu, přepínání za běhu
- `Activity.created_by_id` = kdo úkol zadal, `TimeSession.user_id` = kdo trackoval čas

### **Číselníky:**
- `zadavatele` (BMW, Audi...)
- `projekty` (BMW-2024-001...)
- `obsahy_mereni` (Geometrie, Rozměry...)
- `duvody_mereni` (Před DT, Po DT...)

---

## 🎯 WORKFLOW V KÓDU

### **Start tracking:**
```python
# 1. Uživatel klikne START na aktivitě
activity_card._on_start()

# 2. Získá vybranou fázi z panelu
phase = tracking_panel.get_selected_phase()

# 3. Zavolá main_window.start_tracking()
main_window.start_tracking(activity_id, phase)

# 4. CRUD vytvoří TimeSession
session = crud.start_time_session(db, user_id, activity_id, phase)

# 5. GUI aktualizuje časovač
tracking_panel.update_running_session(session)
```

### **Stop tracking:**
```python
# 1. Uživatel klikne STOP
tracking_panel._on_stop()

# 2. Zavolá main_window.stop_tracking()
main_window.stop_tracking()

# 3. CRUD ukončí session
stopped = crud.stop_time_session(db, session_id)
# → Vypočítá duration_minutes

# 4. GUI vyčistí panel
tracking_panel.clear_running_session()
```

---

## 🐛 ZNÁMÉ LIMITY

1. **Jen jedna běžící session** — automatický stop při startu nové
2. **Žádné editace po vytvoření** — metadata PROJECT_TASK nelze změnit (P2-1)
3. **Žádné mazání** — session ani aktivity nelze smazat přes GUI (P2-3, P2-4)
4. **Žádné statistiky** — data jsou v DB, přehledy zatím neimplementovány (P3)

**Tyto limity nejsou kritické pro MVP, opravíme dle priorit v backlogu!**

---

## 📝 DALŠÍ KROKY

### **Hned teď (P2 — editace dat):**
1. P2-1 Editace metadat PROJECT_TASK po vytvoření
2. P2-3 Mazání chybné session (s potvrzením)
3. P2-4 Archivace / smazání aktivity

### **Střední termín (P3 — statistiky):**
1. P3-2 Denní přehled odpracovaného času
2. P3-1 Statistiky úkolu (čas po fázích, počet přerušení)
3. P3-7 Filtr přehledů per-user (datový model již připraven)

### **Dlouhý termín (P4):**
1. P4-3 Archiv dokončených aktivit
2. P3-6 Export do CSV/Excel
3. P4-4 PostgreSQL migrace (Alembic)

---

## ✅ ZÁVĚR

**MVP je FUNKČNÍ a POUŽITELNÝ!** 🎉

Aplikace pokrývá **klíčový workflow**:
- ✅ Vytvoření PROJECT_TASK s validací vstupů
- ✅ Real-time tracking času s fázemi
- ✅ PAUZA s elapsed time trackingem
- ✅ STOP-OK / STOP-NOK s důvodem invalidace
- ✅ 9 typů ROUTINE aktivit
- ✅ Multi-user — výběr profilu při startu, přepínání za běhu
- ✅ Sdílený seznam úkolů (vidí všichni profily)
- ✅ Potvrzovací dialogy před destruktivními akcemi
- ✅ Centrální logger + live log panel v GUI
- ✅ Pytest testy databázové vrstvy (16 testů)

**Nyní můžeš:**
1. Spustit aplikaci: `python src/main.py`
2. Vytvořit reálné úkoly a trackovat čas
3. Přepínat mezi profily bez restartu

**Další funkce přidáme podle priorit v backlogu!** 🚀
