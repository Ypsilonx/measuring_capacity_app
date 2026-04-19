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
- 2-sloupcový layout (PROJECT_TASKS 80% + ROUTINES 20%) + LogPanel dole
- Desktop aplikace (ne web, ne mobile)

### 7. Logging
- **Nikdy nepoužívej `print()`** — vždy `from src.utils.app_logger import get_logger`
- Logger je singleton — volej `get_logger()` na vrcholu každého modulu
- Úrovně: `logger.info()` pro normální tok, `logger.warning()` pro validační chyby, `logger.error()` pro výjimky
- Log soubor: `data/app.log` (rotující, max 1 MB)

### 8. Dokumentace — pravidlo aktuálnosti
- **Po každé implementované funkci aktualizuj `MVP_STATUS.md`** — přesuň hotové položky do sekce CO JE HOTOVO, aktualizuj záhlaví KDE JSME TEĎ
- Hotové TODO položky v backlogu přeškrtni (`~~text~~`) nebo odstraň, nikdy je nesmazávej bez záznamu
- `PROJECT_CONFIG.md` aktualizuj při změně dev pravidel nebo nové infrastrukturní vrstvy
- `README.md` aktualizuj při změně schématu DB nebo přidání nové funkční oblasti
- **Toto se provádí PŘED každým commitem, ne po — aktualizace .md souborů je součástí každého úkolu**

## Aktuální stav projektu
- [x] KROK 0: Základní setup
- [x] KROK 1: Návrh DB schématu
- [x] KROK 2: MVP aplikace funkční
- [x] Multi-user podpora
- [x] ROUTINES support
- [x] Responzivní design
- [x] Instrukce pro AI asistenta (`.github/instructions/`)
- [x] Logging — `src/utils/app_logger.py` + `LogPanel` v GUI
- [x] P1-1 Validace formulářů — `NewProjectTaskDialog`, TMA reopen logika
- [x] P1-2 Potvrzovací dialogy — `ConfirmDialog`
- [x] P1-4 Pytest testy — `tests/test_crud.py`, 16 testů
- [x] GUI-1 Toolbar — datum, uživatel, přepínání uživatele za běhu
- [ ] P2–P4 viz MVP_STATUS.md backlog

## Kde najdeš co

| Soubor | Obsah |
|--------|-------|
| [README.md](README.md) | Přehled projektu, schéma DB, workflow |
| [QUICKSTART.md](QUICKSTART.md) | Jak spustit, seed data, ovládání |
| [MVP_STATUS.md](MVP_STATUS.md) | Aktuální stav + TODO backlog s prioritami |
| [PROJECT_CONFIG.md](PROJECT_CONFIG.md) | Tento soubor — dev pravidla a příkazy |
| [.github/instructions/](`.github/instructions/`) | Konvence pro AI asistenta (architektura, DB, GUI) |
| [src/utils/app_logger.py](src/utils/app_logger.py) | Singleton logger — použij `get_logger()` |
| [data/app.log](data/app.log) | Rotující log soubor (runtime, není v gitu) |
