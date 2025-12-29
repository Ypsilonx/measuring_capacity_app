"""
Script pro naplnění databáze testovacími daty.

Vytvoří:
- Základní číselníky (zadavatelé, projekty, důvody...)
- 2-3 testovací PROJECT_TASK aktivity
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.database import init_db, SessionLocal
from src.database import crud, models

def seed_database():
    """Naplní databázi testovacími daty."""
    
    print("=" * 60)
    print("SEED DATABASE - Testovací data")
    print("=" * 60)
    
    init_db()
    db = SessionLocal()
    
    try:
        # 1. Vytvoř uživatele
        print("\n1️⃣  Vytváření uživatele...")
        user = crud.get_user_by_username(db, "admin")
        if not user:
            user = crud.create_user(db, username="admin", full_name="Administrator")
            print(f"✅ User: {user.username}")
        else:
            print(f"ℹ️  User již existuje: {user.username}")
        
        # 2. Vytvoř zadavatele
        print("\n2️⃣  Vytváření zadavatelů...")
        zadavatele_data = [
            {"name": "BMW", "email": "kontakt@bmw.de"},
            {"name": "Audi", "email": "info@audi.com"},
            {"name": "Škoda Auto", "email": "contact@skoda.cz"},
        ]
        
        zadavatele = {}
        for data in zadavatele_data:
            existing = crud.get_lookup_item_by_name(db, models.Zadavatel, data["name"])
            if not existing:
                item = crud.create_lookup_item(db, models.Zadavatel, **data)
                zadavatele[data["name"]] = item
                print(f"   ✅ {data['name']}")
            else:
                zadavatele[data["name"]] = existing
                print(f"   ℹ️  {data['name']} (existuje)")
        
        # 3. Vytvoř projekty (BEZ zadavatele - odpojené)
        print("\n3️⃣  Vytváření projektů...")
        projekty_data = [
            {"code": "BMW-2024-001", "name": "Série 5 - Testování geometrie"},
            {"code": "AUDI-2024-015", "name": "A4 - Kontrola rozměrů"},
            {"code": "SKODA-2024-042", "name": "Octavia - Validace dílů"},
        ]
        
        projekty = {}
        for data in projekty_data:
            existing = crud.get_lookup_item_by_name(db, models.Projekt, data["name"])
            if not existing:
                item = crud.create_lookup_item(
                    db, 
                    models.Projekt,
                    code=data["code"],
                    name=data["name"]
                )
                projekty[data["code"]] = item
                print(f"   ✅ {data['code']}")
            else:
                projekty[data["code"]] = existing
                print(f"   ℹ️  {data['code']} (existuje)")
        
        # 4. ObsahMereni je teď ENUM (ne tabulka) - přeskočit
        print("\n4️⃣  Obsah měření je ENUM (FREEPLAY, FUNCTION, OSTATNÍ) - skip...")
        
        # 5. Vytvoř důvody měření
        print("\n5️⃣  Vytváření důvodů měření...")
        duvody_data = ["Před DT", "Během DT", "Po DT", "Přeměření", "Reklamace"]
        
        duvody = {}
        for name in duvody_data:
            existing = crud.get_lookup_item_by_name(db, models.DuvodMereni, name)
            if not existing:
                item = crud.create_lookup_item(db, models.DuvodMereni, name=name)
                duvody[name] = item
                print(f"   ✅ {name}")
            else:
                duvody[name] = existing
                print(f"   ℹ️  {name} (existuje)")
        
        # 6. Vytvoř testovací PROJECT_TASK aktivity
        print("\n6️⃣  Vytváření testovacích aktivit...")
        
        activities_data = [
            {
                "tma_cislo": "TMA-2025-001",
                "nazev_testu": "BMW Série 5 - Měření přední kapoty",
                "zadavatel": "BMW",
                "projekt": "BMW-2024-001",
                "obsah": models.ObsahMereniType.FUNCTION,
                "duvod": "Před DT",
                "pocet_ks": 15
            },
            {
                "tma_cislo": "TMA-2025-002",
                "nazev_testu": "Audi A4 - Kontrola dveří",
                "zadavatel": "Audi",
                "projekt": "AUDI-2024-015",
                "obsah": models.ObsahMereniType.FREEPLAY,
                "duvod": "Během DT",
                "pocet_ks": 8
            },
            {
                "tma_cislo": "TMA-2025-003",
                "nazev_testu": "Škoda Octavia - Validace nárazníku",
                "zadavatel": "Škoda Auto",
                "projekt": "SKODA-2024-042",
                "obsah": models.ObsahMereniType.OSTATNI,
                "duvod": "Přeměření",
                "pocet_ks": 12
            }
        ]
        
        for data in activities_data:
            # Zkontroluj, zda aktivita již neexistuje
            existing_activities = crud.get_activities(db, limit=1000)
            existing = next((a for a in existing_activities if a.tma_cislo == data["tma_cislo"]), None)
            
            if not existing:
                activity_data = {
                    'type': models.ActivityType.PROJECT_TASK,
                    'tma_cislo': data["tma_cislo"],
                    'nazev_testu': data["nazev_testu"],
                    'zadavatel_id': zadavatele[data["zadavatel"]].id,
                    'projekt_id': projekty[data["projekt"]].id,
                    'obsah_mereni': data["obsah"],  # ENUM přímo
                    'duvod_mereni_id': duvody[data["duvod"]].id,
                    'pocet_ks': data["pocet_ks"],
                    'created_by_id': user.id  # Vytvořený uživatel
                }
                
                activity = crud.create_activity(db, activity_data)
                print(f"   ✅ Vytvořena aktivita: {activity.nazev_testu}")
            else:
                print(f"   ⏭️  Aktivita {data['tma_cislo']} již existuje, přeskakuji")
        
        print("\n" + "=" * 60)
        print("✅ DATABÁZE NAPLNĚNA TESTOVACÍMI DATY!")
        print("=" * 60)
        print("\n💡 Teď můžeš spustit aplikaci: python src/main.py")
        
    except Exception as e:
        print(f"\n❌ CHYBA: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
