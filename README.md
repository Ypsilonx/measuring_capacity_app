# Measuring Capacity App

Desktop aplikace pro měření a sledování času stráveného nad pracovními úkoly s predikcí na základě historických dat.

## Technologie
- Python 3.13+
- SQLite + SQLAlchemy (ORM) - s možností migrace na PostgreSQL
- CustomTkinter (GUI)
- Pandas, Matplotlib, Plotly (grafy a analýzy)

## Struktura projektu
```
measuring_capacity_app/
├── src/
│   ├── database/      # DB modely a operace
│   ├── gui/           # CustomTkinter GUI
│   ├── core/          # Business logika
│   └── utils/         # Pomocné funkce
├── tests/             # Testy
├── venv/              # Virtual environment
└── requirements.txt
```

## Koncept aplikace

### Workflow
1. **Plánování aktivit** - vytváření ROUTINE (oběd, přestávka, meeting) a PROJECT_TASK (měřitelné úkoly)
2. **Tracking času** - Start/Stop měření s možností přerušení a pokračování i další dny
3. **Fázové měření** - každá PROJECT_TASK má fáze: Příprava, Měření, Úklid
4. **Validace dat** - možnost označit TimeSession jako chybný (is_valid = FALSE)
5. **Analýzy a predikce** - grafy, statistiky, odhady času na základě historie

### Typy aktivit

**ROUTINE aktivity:**
- Každodenní, neprojektové: Oběd, WC, Kouření, Káva, Přestávka, Meeting, Porady
- Jednoduché tracking bez fází

**PROJECT_TASK aktivity:**
- Měřitelné projektové úkoly s metadaty:
  - Zadavatel
  - Projekt
  - TMA číslo
  - Název testu
  - Obsah měření
  - Počty kusů
  - Důvod měření (před DT, po DT, přeměření...)
  - Poznámky
- Tracking po fázích (Příprava → Měření → Úklid)

## Databázové schéma

### Hlavní tabulky

**User** - uživatelé
```
- id (PK)
- username
- full_name
- created_at
```

**Activity** - definice aktivit (master záznamy)
```
- id (PK)
- type: ENUM ('ROUTINE', 'PROJECT_TASK')
- name (pro ROUTINE: "Oběd", "Káva"...)

-- PROJECT_TASK fields (nullable) --
- zadavatel_id (FK → Zadavatel)
- projekt_id (FK → Projekt)
- tma_cislo
- nazev_testu
- obsah_mereni_id (FK → ObsahMereni)
- pocet_ks
- duvod_mereni_id (FK → DuvodMereni)

- status: ENUM ('ACTIVE', 'COMPLETED')
- created_by (FK → User)
- created_at
- updated_at
```

**TimeSession** - časové záznamy (co se skutečně stalo)
```
- id (PK)
- activity_id (FK → Activity)
- user_id (FK → User)
- start_time (datetime)
- end_time (datetime, nullable - pokud probíhá)
- duration_minutes (computed při end_time)
- phase: ENUM ('Příprava', 'Měření', 'Úklid') - nullable pro ROUTINE
- is_valid (boolean, default TRUE) - pro označení chybných měření
- invalidation_reason (text) - proč je neplatný
- notes (text)
- created_at
```

### Číselníky (lookup tables)

**Zadavatel**
```
- id (PK)
- name
- email
```

**Projekt**
```
- id (PK)
- code
- name
- zadavatel_id (FK)
```

**DuvodMereni**
```
- id (PK)
- name (před DT, během DT, po DT, přeměření...)
```

**ObsahMereni**
```
- id (PK)
- name
```

### Klíčové koncepty

**Přerušení a pokračování:**
- Activity může mít více TimeSessions (různé dny, přerušení)
- Každá fáze = samostatná TimeSession
- TimeSession.end_time = NULL znamená "právě probíhá"

**Chybná měření:**
- TimeSession.is_valid = FALSE
- Predikce a grafy filtrují jen validní: `WHERE is_valid = TRUE`
- Historie uchovává vše pro audit

**Různé důvody měření:**
- Aktivity se stejnými parametry ale různými důvody = separátní Activity záznamy
- Umožňuje samostatné normy/predikce pro "před DT" vs "po DT"

## Instalace

### 1. Vytvoření virtuálního prostředí
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 2. Instalace Python závislostí
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Konfigurace databáze
Zkopírovat `.env.example` na `.env`:
```bash
copy .env.example .env
```

Pro SQLite (default) není potřeba nic měnit - databáze se vytvoří automaticky v `data/measuring_capacity.db`

**Migrace na PostgreSQL (volitelné, později):**
- Instalovat PostgreSQL z https://www.postgresql.org/download/windows/
- Vytvořit databázi `measuring_capacity_db`
- Upravit `.env`: nastavit DB_TYPE=postgresql a vyplnit credentials

## Spuštění
```bash
.\venv\Scripts\Activate.ps1
python src/main.py
```

## Funkce
- ✅ Tracking času s Start/Stop pro aktivity
- ✅ Fázové měření (Příprava, Měření, Úklid)
- ✅ Přerušení a pokračování úkolů napříč dny
- ✅ Validace/invalidace časových záznamů
- ✅ ROUTINE vs PROJECT_TASK aktivity
- ✅ Číselníky pro konzistentní data (projekty, zadavatelé...)
- ✅ Historie všech měření
- ✅ Dashboard s grafy a filtrováním
- ✅ Predikce času na základě historických dat
- ✅ Podpora více uživatelů
