# 📊 MVP - PŘEHLED PROJEKTU

## ✅ CO JE HOTOVO (29.12.2025)

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

**Soubory:**
- [src/gui/user_selection_dialog.py](src/gui/user_selection_dialog.py)
- [src/gui/planner_window.py](src/gui/planner_window.py)
- [src/gui/tracking_dialog.py](src/gui/tracking_dialog.py)
- [src/gui/routine_dialog.py](src/gui/routine_dialog.py)
- [src/gui/new_project_task_dialog.py](src/gui/new_project_task_dialog.py)
- [src/gui/input_dialog.py](src/gui/input_dialog.py)

### **3. Pomocné scripty**
- ✅ [scripts/test_database.py](scripts/test_database.py) - Test DB bez GUI
- ✅ [scripts/seed_database.py](scripts/seed_database.py) - Naplnění testovacími daty

### **4. Dokumentace**
- ✅ [README.md](README.md) - Hlavní dokumentace
- ✅ [QUICKSTART.md](QUICKSTART.md) - Rychlý start MVP
- ✅ [PROJECT_CONFIG.md](PROJECT_CONFIG.md) - Konfigurace projektu
- ✅ Tento přehled (MVP_STATUS.md)

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

## ❌ CO JEŠTĚ CHYBÍ (Příští iterace)

### **Priorita 1 - Statistiky a analýzy:**
- ❌ Dashboard s grafy
- ❌ Graf: rozdělení času podle fází
- ❌ Statistiky pro úkol (průměrná session, nejdelší/nejkratší)
- ❌ Denní/týdenní přehledy
- ❌ Predikce času na základě historie

### **Priorita 2 - Pokročilé funkce:**
- ❌ Editace poznámek k existující session
- ❌ Editace aktivit
- ❌ Mazání sessions/aktivit
- ❌ Export dat (CSV, Excel)
- ❌ Filtrování a vyhledávání

### **Priorita 3 - Kvalita:**
- ❌ Error handling a validace formulářů
- ❌ Potvrzovací dialogy pro destruktivní akce
- ❌ Testy (pytest)
- ❌ Logging
- ❌ Migrace na PostgreSQL (volitelné)

---

## 📈 STATISTIKY

### **Kód:**
```
Celkem řádků:   ~1500 LOC
Python soubory: 9 souborů
GUI komponenty: 4 soubory
DB operace:     ~20 CRUD funkcí
```

### **Databáze:**
```
Tabulky:        8 tabulek
  - users (1)
  - activities (1)
  - time_sessions (1)
  - Číselníky (5)

Relationships:  Plně mapované (SQLAlchemy ORM)
```

### **GUI:**
```
Hlavní okno:    1200x700 px
Panely:         2 (seznam + tracking)
Widgety:        ~30+ CustomTkinter prvků
Dark mode:      ✅
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
