# 📊 STAV PROJEKTU — measuring_capacity_app

> Naposledy aktualizováno: 19.4.2026

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

**Aktuální zaměření:** Priorita P1 dokončena. Zbývají P2–P4 backlog nebo další GUI vylepšení.

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

**Soubory:**
- [src/database/models.py](src/database/models.py) - DB modely s ENUMs
- [src/database/database.py](src/database/database.py) - Engine & session
- [src/database/crud.py](src/database/crud.py) - CRUD operace

### **2. GUI vrstva** (MVP kompletní + vylepšení)
- ✅ CustomTkinter desktop aplikace (dark mode)
- ✅ UserSelectionDialog - výběr uživatele při startu
- ✅ PlannerWindow - hlavní okno se 2 panely:
  - PROJECT_TASKS panel (80% šířky) s TaskCard widgety
  - ROUTINES panel (20% šířky) s 9 quick-action tlačítky
- ✅ TaskCard s rámečky a rozbalovacím seznamem sessions:
  - Zobrazení validních i invalidních sessions
  - Ikony ✅/❌ podle validity
  - Důvod invalidace v závorce
  - Poslední fáze v souhrnu
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
- [src/gui/user_selection_dialog.py](src/gui/user_selection_dialog.py)
- [src/gui/planner_window.py](src/gui/planner_window.py)
- [src/gui/tracking_dialog.py](src/gui/tracking_dialog.py)
- [src/gui/routine_dialog.py](src/gui/routine_dialog.py)
- [src/gui/new_project_task_dialog.py](src/gui/new_project_task_dialog.py)
- [src/gui/input_dialog.py](src/gui/input_dialog.py)
- [src/gui/log_panel.py](src/gui/log_panel.py)

### **3. Pomocné scripty**
- ✅ [scripts/test_database.py](scripts/test_database.py) - Test DB bez GUI
- ✅ [scripts/seed_database.py](scripts/seed_database.py) - Naplnění testovacími daty

### **4. Infrastruktura — Logging**
- ✅ `src/utils/app_logger.py` — singleton `get_logger()`, RotatingFileHandler, GUI dispatch
- ✅ `data/app.log` — rotující log soubor (max 1 MB, 3 zálohy)
- ✅ `src/gui/confirm_dialog.py` — znovupoužitelný `ConfirmDialog` (title, message, tlačítka, barvy)
- ✅ `src/gui/log_panel.py` — `LogPanel` widget ve spodní části `PlannerWindow`
- ✅ `tests/test_crud.py` — 16 pytest testů (User, Activity, TimeSession), in-memory SQLite

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
| P2-1 | Editace aktivity | Možnost změnit metadata PROJECT_TASK po vytvoření |
| P2-2 | Editace poznámek session | Přidat/změnit `notes` u existující TimeSession |
| P2-3 | Mazání session | Smazat chybnou session (s potvrzením) |
| P2-4 | Mazání aktivity | Archivace nebo smazání celé aktivity |

### 🟢 Priorita 3 — Statistiky a analytika (hlavní přidaná hodnota)

| # | Úkol | Popis |
|---|------|-------|
| P3-1 | Statistiky úkolu | Průměrná délka session, celkový čas po fázích, počet přerušení |
| P3-2 | Denní přehled | Kolik hodin odpracováno dnes (PROJECT_TASK + ROUTINE breakdown) |
| P3-3 | Týdenní přehled | Agregovaný přehled po dnech, graf |
| P3-4 | Fázový breakdown | Graf: kolik % času Příprava / Měření / Úklid pro daný úkol |
| P3-5 | Predikce | Odhad zbývajícího času na základě historických dat stejného typu |
| P3-6 | Export dat | Export do CSV/Excel (Pandas) |

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
Celkem řádků:   ~1500 LOC
Python soubory: 9 souborů src/ + 2 skripty
GUI komponenty: 7 souborů
DB operace:     ~20 CRUD funkcí
Tabulky DB:     8 (users, activities, time_sessions + 5 číselníků)
Instrukce AI:   3 soubory .github/instructions/
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
│   ├── main.py                 # Vstupní bod ✅
│   │
│   ├── database/               # Databázová vrstva ✅
│   │   ├── models.py           # SQLAlchemy modely
│   │   ├── database.py         # Engine & session
│   │   └── crud.py             # CRUD operace
│   │
│   ├── gui/                    # GUI vrstva ✅
│   │   ├── main_window.py      # Hlavní okno
│   │   ├── tracking_panel.py   # Tracking panel
│   │   ├── activity_list.py    # Seznam aktivit
│   │   └── new_activity_dialog.py  # Dialog
│   │
│   ├── core/                   # Business logika ❌ (prázdné)
│   └── utils/                  # Pomocné funkce ❌ (prázdné)
│
├── scripts/                    # Pomocné scripty ✅
│   ├── test_database.py
│   └── seed_database.py
│
├── data/                       # SQLite databáze ✅
│   └── measuring_capacity.db
│
├── tests/                      # Testy ❌ (prázdné)
│
├── venv/                       # Virtual environment ✅
│
├── requirements.txt            # Závislosti ✅
├── .env                        # Konfigurace ✅
├── README.md                   # Hlavní docs ✅
├── QUICKSTART.md               # Rychlý start ✅
└── PROJECT_CONFIG.md           # Config ✅
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
- pytest (testy - zatím neimplementováno)
- black (formatting - zatím neimplementováno)

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
- Zatím hardcoded "admin"
- Připraveno pro multi-user

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

1. **Jen jedna běžící session** - automatický stop při startu nové
2. **Žádná validace formuláře** - může způsobit chyby
3. **Potvrzení dokončení** - používá InputDialog (není ideální)
4. **Žádný error handling** - chyby jen v konzoli
5. **Žádné testy** - jen manuální testování
6. **Hardcoded admin user** - není přihlašování

**Tyto limity nejsou kritické pro MVP, opravíme později!**

---

## 📝 DALŠÍ KROKY

### **Hned teď:**
1. ✅ MVP je funkční
2. 🔲 Otestuj reálný workflow
3. 🔲 Identifikuj priority

### **Krátký termín:**
1. Zobrazení historie session pro aktivitu
2. Invalidace session s důvodem
3. Lepší error handling

### **Střední termín:**
1. Graf: čas podle fází
2. Plánování dne
3. ROUTINE aktivity

### **Dlouhý termín:**
1. Predikce času
2. Export dat
3. Multi-user support
4. PostgreSQL migrace

---

## ✅ ZÁVĚR

**MVP je FUNKČNÍ a POUŽITELNÝ!** 🎉

Aplikace pokrývá **klíčový workflow**:
- ✅ Vytvoření PROJECT_TASK
- ✅ Real-time tracking času
- ✅ Fázové měření s variabilitou
- ✅ Přerušení a pokračování
- ✅ Sumarizace času
- ✅ Nedokončené aktivity zůstávají aktivní

**Nyní můžeš:**
1. Spustit aplikaci: `python src/main.py`
2. Vytvořit reálné úkoly
3. Trackovat čas
4. Získat přehled o čase stráveném na úkolech

**Další funkce přidáme podle priorit!** 🚀
