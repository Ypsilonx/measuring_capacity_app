# PROJEKTOVÁ KONFIGURACE - INTERNÍ

## ⚠️ KRITICKÁ PRAVIDLA PRO TENTO PROJEKT

### 1. VŽDY POUŽÍVAT VENV
- **KAŽDÝ Python příkaz musí běžet ve venv!**
- Aktivace: `.\venv\Scripts\Activate.ps1` (Windows PowerShell)
- Kontrola: `where python` nebo `python --version`

### 2. Instalace balíčků
- **JEN přes aktivovaný venv!**
- Nikdy globálně!
- Příkaz: `.\venv\Scripts\Activate.ps1; pip install -r requirements.txt`

### 3. Spouštění aplikace
- Vždy: `.\venv\Scripts\Activate.ps1; python src/main.py`

### 4. Databáze
- SQLite (výchozí) + SQLAlchemy ORM
- Možnost migrace na PostgreSQL
- Žádné ruční SQL queries
- Konfigurace v `.env`

### 5. Struktura dat
- Hierarchická: Activity → Many TimeSessions
- Jeden úkol může mít desítky časových záznamů
- Podpora PAUZA s elapsed time tracking
- ENUM typy pro ObsahMereni a RoutineType

### 6. GUI
- CustomTkinter (dark mode)
- Responzivní design pro různá rozlišení
- 2-sloupcový layout (PROJECT_TASKS 80% + ROUTINES 20%)
- Desktop aplikace (ne web, ne mobile)

## Aktuální stav projektu
- [x] KROK 0: Základní setup
- [x] KROK 1: Návrh DB schématu
- [x] KROK 2: MVP aplikace funkční
- [x] Multi-user podpora
- [x] ROUTINES support
- [x] Responzivní design
- [x] Instrukce pro AI asistenta (`.github/instructions/`)
- [ ] Error handling a validace — viz MVP_STATUS.md P1
- [ ] Statistiky a analytika — viz MVP_STATUS.md P3

## Kde najdeš co

| Soubor | Obsah |
|--------|-------|
| [README.md](README.md) | Přehled projektu, schéma DB, workflow |
| [QUICKSTART.md](QUICKSTART.md) | Jak spustit, seed data, ovládání |
| [MVP_STATUS.md](MVP_STATUS.md) | Aktuální stav + TODO backlog s prioritami |
| [PROJECT_CONFIG.md](PROJECT_CONFIG.md) | Tento soubor — dev pravidla a příkazy |
| [.github/instructions/](`.github/instructions/`) | Konvence pro AI asistenta (architektura, DB, GUI) |
