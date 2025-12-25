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
- PostgreSQL + SQLAlchemy ORM
- Žádné ruční SQL queries
- Konfigurace v `.env`

### 5. Struktura dat
- Hierarchická: Task → Many TimeSessions
- Jeden úkol může mít desítky časových záznamů
- Podpora přerušení a pokračování úkolů

### 6. GUI
- CustomTkinter
- Grafy: matplotlib + plotly
- Desktop aplikace (ne web, ne mobile)

## Aktuální stav projektu
- [x] KROK 0: Základní setup dokončen
- [ ] KROK 1: Návrh DB schématu
- [ ] Instalace závislostí ve venv

## Poznámky
- Uživatel chce minimalistický přístup - nedělat nic navíc
- Testovat každý krok před pokračováním
- README aktualizovat průběžně
