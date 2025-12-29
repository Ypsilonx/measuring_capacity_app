# 📊 MVP - PŘEHLED PROJEKTU

## ✅ CO JE HOTOVO (29.12.2025)

### **1. Databázová vrstva** (100%)
- ✅ SQLAlchemy ORM modely
- ✅ SQLite databáze
- ✅ CRUD operace pro všechny entity
- ✅ Podpora pro:
  - PROJECT_TASK aktivity
  - Fázové měření (Příprava/Měření/Úklid)
  - Více TimeSession na aktivitu
  - Validace session (`is_valid` flag)
  - Číselníky (Zadavatelé, Projekty, Obsahy, Důvody)

**Soubory:**
- [src/database/models.py](src/database/models.py) - DB modely
- [src/database/database.py](src/database/database.py) - Engine & session
- [src/database/crud.py](src/database/crud.py) - CRUD operace

### **2. GUI vrstva** (MVP kompletní)
- ✅ CustomTkinter desktop aplikace
- ✅ 2-panelový layout (seznam + tracking)
- ✅ Real-time časovač
- ✅ Formulář pro novou aktivitu
- ✅ Seznam aktivních úkolů s detaily
- ✅ Start/Stop tracking s výběrem fáze

**Soubory:**
- [src/gui/main_window.py](src/gui/main_window.py) - Hlavní okno
- [src/gui/tracking_panel.py](src/gui/tracking_panel.py) - Tracking panel
- [src/gui/activity_list.py](src/gui/activity_list.py) - Seznam aktivit
- [src/gui/new_activity_dialog.py](src/gui/new_activity_dialog.py) - Dialog pro nový úkol

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
- ✅ Jeden úkol = mnoho session (i ve stejné fázi)
- ✅ Přerušení a pokračování přes víc dní
- ✅ Změna fází kdykoliv
- ✅ Živý časovač s real-time zobrazením
- ✅ Sumarizace validního času
- ✅ Aktivní úkoly zůstávají v seznamu

---

## ❌ CO JEŠTĚ CHYBÍ (Příští iterace)

### **Priorita 1 - Validace a historie:**
- ❌ Zobrazení všech session pro aktivitu
- ❌ Invalidace session (označení jako chybný) + důvod
- ❌ Editace poznámek k existující session

### **Priorita 2 - Analytika:**
- ❌ Graf: rozdělení času podle fází
- ❌ Statistiky pro úkol (průměrná session, nejdelší/nejkratší)
- ❌ Predikce času na základě historie

### **Priorita 3 - Plánování:**
- ❌ Plánování dne (morning planning)
- ❌ ROUTINE aktivity (oběd, pauzy...)
- ❌ Denní přehled (co se stalo dnes)

### **Priorita 4 - Kvalita:**
- ❌ Error handling a validace
- ❌ Potvrzovací dialogy
- ❌ Export dat (CSV, Excel)
- ❌ Testy (pytest)

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
