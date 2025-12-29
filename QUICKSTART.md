# 🚀 RYCHLÝ START - MVP Aplikace

## ✅ Co je hotové (MVP)

**Funkční desktop aplikace** s těmito funkcemi:

### 📋 **Hlavní funkce:**
- ✅ **Vytvoření PROJECT_TASK** - formulář s TMA, název testu, projekt, zadavatel...
- ✅ **Start/Stop tracking** - real-time měření času s živým časovačem
- ✅ **Fázové měření** - výběr fáze (Příprava/Měření/Úklid) před startem
- ✅ **Seznam aktivních úkolů** - přehled všech ACTIVE aktivit
- ✅ **Sumarizace času** - zobrazení celkového času a počtu session
- ✅ **Dokončení úkolu** - změna statusu na COMPLETED

### 🎯 **Workflow:**
1. Klikni "➕ Nový úkol" → vyplň formulář
2. Vyber úkol ze seznamu → vyber fázi → klikni "▶️ START"
3. Živý časovač běží
4. Klikni "⏹️ STOP" → session se uloží
5. Opakuj podle potřeby (i další den)
6. Klikni "✅ Dokončit" když je úkol hotový

---

## 🏃 Spuštění aplikace

### 1️⃣ **Naplnění testovacími daty** (volitelné, ale doporučené)
```powershell
# Aktivuj venv
.\venv\Scripts\Activate.ps1

# Spusť seed script
python scripts/seed_database.py
```

**Vytvoří:**
- 3 zadavatele (BMW, Audi, Škoda)
- 3 projekty
- 4 obsahy měření
- 5 důvodů měření
- 3 testovací úkoly (PROJECT_TASK)

### 2️⃣ **Spuštění aplikace**
```powershell
# Aktivuj venv (pokud ještě není)
.\venv\Scripts\Activate.ps1

# Spusť aplikaci
python src/main.py
```

**Otevře se GUI okno** s:
- **Levý panel:** Seznam aktivních úkolů
- **Pravý panel:** Tracking panel s časovačem

---

## 📸 Co uvidíš

### **Prázdný stav** (bez dat):
```
┌─────────────────────────────────────┐
│ 📋 Aktivní úkoly (PROJECT_TASK)     │
│                                     │
│  ┌─────────────────────────┐        │
│  │  ➕ Nový úkol            │        │
│  └─────────────────────────┘        │
│                                     │
│     📭 Žádné aktivní úkoly          │
│     Klikni na '➕ Nový úkol'        │
└─────────────────────────────────────┘
```

### **S testovacími daty:**
```
┌──────────────────────────────────────────────┬──────────────────────┐
│ 📋 Aktivní úkoly (PROJECT_TASK)              │  ⏱️ Tracking času    │
│                                              │                      │
│  ┌──────────────────────────┐                │  Status: Žádný       │
│  │  ➕ Nový úkol             │                │  00:00:00            │
│  └──────────────────────────┘                │                      │
│                                              │  Fáze:               │
│  🏷️ TMA-2024-1234                           │  ⚪ Příprava         │
│  📝 BMW Série 5 - Měření přední kapoty      │  ⚫ Měření           │
│  📁 BMW-2024-001                             │  ⚪ Úklid            │
│  👤 BMW                                      │                      │
│  ⏱️ Celkový čas: 0h 0min (0 session)        │  ⏹️ STOP (disabled)  │
│  [▶️ START] [✅ Dokončit]                    │                      │
│                                              │  💡 Start tracking:  │
│  🏷️ TMA-2024-5678                           │  Vyber úkol vlevo   │
│  📝 Audi A4 - Kontrola dveří                │                      │
│  ...                                         │                      │
└──────────────────────────────────────────────┴──────────────────────┘
```

---

## 🎮 Jak používat

### **Vytvoření nového úkolu:**
1. Klikni "➕ Nový úkol"
2. Vyplň:
   - TMA číslo (povinné)
   - Název testu (povinné)
   - Zadavatel (dropdown nebo přidej nového)
   - Projekt (dropdown nebo přidej nový)
   - Obsah měření
   - Důvod měření
   - Počet kusů
3. Klikni "✅ Vytvořit"

### **Start tracking:**
1. Vyber úkol ze seznamu (kartu)
2. Vyber fázi v pravém panelu (Příprava/Měření/Úklid)
3. Klikni "▶️ START" na kartě úkolu
4. Časovač začne běžet
5. Status: "🟢 TRACKING AKTIVNÍ"

### **Stop tracking:**
1. Klikni "⏹️ STOP" v pravém panelu
2. Session se uloží do databáze
3. Čas se přičte k celkovému času úkolu

### **Dokončení úkolu:**
1. Klikni "✅ Dokončit" na kartě úkolu
2. Potvrdí se dialog
3. Úkol zmizí ze seznamu (status → COMPLETED)

---

## 🗄️ Databáze

**Lokace:** `data/measuring_capacity.db` (SQLite)

**Tabulky:**
- `users` - uživatelé
- `activities` - úkoly (ROUTINE / PROJECT_TASK)
- `time_sessions` - časové záznamy
- `zadavatele` - číselník zadavatelů
- `projekty` - číselník projektů
- `obsahy_mereni` - číselník obsahů
- `duvody_mereni` - číselník důvodů

---

## 🧪 Testování

### **Ruční test workflow:**
```powershell
# 1. Naplň data
python scripts/seed_database.py

# 2. Spusť aplikaci
python src/main.py

# 3. Vyzkoušej:
#    - Vytvoř nový úkol
#    - Start tracking na existujícím úkolu
#    - Nech běžet 10 sekund
#    - Stop tracking
#    - Zkontroluj, že čas se zobrazil
#    - Start znovu (jiná fáze)
#    - Dokončit úkol
```

### **DB test (bez GUI):**
```powershell
python scripts/test_database.py
```

---

## ❌ Co ještě NENÍ implementováno

- ❌ Invalidace session (označení jako chybný)
- ❌ Editace session poznámek
- ❌ Grafy a statistiky
- ❌ Predikce času
- ❌ Export dat
- ❌ Plánování dne
- ❌ ROUTINE aktivity (jen PROJECT_TASK)
- ❌ Historie session (zobrazení všech session)
- ❌ Filtry a vyhledávání

**Tyto funkce přidáme postupně podle potřeby!** 🚀

---

## 🐛 Známé problémy

1. **Potvrzovací dialog pro Dokončit** - je příliš jednoduchý (CTkInputDialog místo potvrzení)
2. **Žádná validace formuláře** - prázdné combobox hodnoty mohou způsobit chybu
3. **Žádný error handling** - chyby se jen vypisují do konzole

**Opravíme v další iteraci!**

---

## 💡 Tipy

- **Aplikace pamatuje běžící session** - pokud necháš session běžet a zavřeš aplikaci, po novém spuštění se session obnoví
- **Můžeš mít jen 1 session běžící** - start nové automaticky zastaví předchozí
- **Úkoly zůstávají ACTIVE** dokud je ručně nedokončíš
- **Testovací data můžeš vytvořit opakovaně** - script kontroluje duplicity

---

## 📝 Další kroky (TODO)

1. ✅ MVP aplikace (HOTOVO!)
2. 🔲 Zobrazení historie session pro úkol
3. 🔲 Invalidace session + důvod
4. 🔲 Editace poznámek k session
5. 🔲 Graf: rozdělení času podle fází
6. 🔲 Plánování dne (morning planning)
7. 🔲 ROUTINE aktivity support
8. 🔲 Predikce času podle historie

**Prioritizujeme podle tvých potřeb!** 🎯
