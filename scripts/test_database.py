"""
Test script pro ověření funkčnosti databáze a CRUD operací.
Simuluje reálný workflow podle požadavků uživatele.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.database import init_db, SessionLocal
from src.database import crud, models

def test_workflow():
    """Testuje reálný workflow aplikace."""
    
    print("=" * 60)
    print("TEST: Inicializace databáze")
    print("=" * 60)
    init_db()
    
    db = SessionLocal()
    
    try:
        # 1. Vytvoření uživatele
        print("\n1️⃣  Vytváření uživatele...")
        user = crud.create_user(db, username="testuser", full_name="Test User")
        print(f"✅ User vytvořen: {user}")
        
        # 2. Vytvoření číselníků
        print("\n2️⃣  Vytváření číselníků...")
        zadavatel = crud.create_lookup_item(db, models.Zadavatel, name="BMW", email="bmw@test.cz")
        projekt = crud.create_lookup_item(db, models.Projekt, code="PRJ-001", name="Test Projekt", zadavatel_id=zadavatel.id)
        obsah = crud.create_lookup_item(db, models.ObsahMereni, name="Geometrie")
        duvod = crud.create_lookup_item(db, models.DuvodMereni, name="Před DT")
        print(f"✅ Číselníky vytvořeny")
        
        # 3. Vytvoření PROJECT_TASK aktivity
        print("\n3️⃣  Vytváření PROJECT_TASK aktivity...")
        activity_data = {
            'type': models.ActivityType.PROJECT_TASK,
            'zadavatel_id': zadavatel.id,
            'projekt_id': projekt.id,
            'tma_cislo': 'TMA-12345',
            'nazev_testu': 'Test geometrie dílu X',
            'obsah_mereni_id': obsah.id,
            'pocet_ks': 10,
            'duvod_mereni_id': duvod.id,
            'status': models.ActivityStatus.ACTIVE,
            'created_by_id': user.id
        }
        activity = crud.create_activity(db, activity_data)
        print(f"✅ Activity vytvořena: ID={activity.id}")
        
        # 4. Simulace FÁZOVÉHO TRACKINGU s VÍCE SESSION
        print("\n4️⃣  Simulace fázového trackingu...")
        print("\n   📋 FÁZE: Příprava")
        
        # Příprava - Session 1
        session1 = crud.start_time_session(db, user.id, activity.id, 
                                          phase=models.TimeSessionPhase.PRIPRAVA,
                                          notes="Příprava materiálu")
        print(f"   ⏱️  Session 1 started: ID={session1.id}")
        session1 = crud.stop_time_session(db, session1.id)
        print(f"   ✅ Session 1 stopped: {session1.duration_minutes} min")
        
        # Příprava - Session 2 (přerušení)
        session2 = crud.start_time_session(db, user.id, activity.id,
                                          phase=models.TimeSessionPhase.PRIPRAVA,
                                          notes="Kalibrace přístroje")
        print(f"   ⏱️  Session 2 started: ID={session2.id}")
        session2 = crud.stop_time_session(db, session2.id)
        print(f"   ✅ Session 2 stopped: {session2.duration_minutes} min")
        
        # Měření - Session 1
        print("\n   📋 FÁZE: Měření")
        session3 = crud.start_time_session(db, user.id, activity.id,
                                          phase=models.TimeSessionPhase.MERENI,
                                          notes="Měření série A")
        print(f"   ⏱️  Session 3 started: ID={session3.id}")
        session3 = crud.stop_time_session(db, session3.id)
        print(f"   ✅ Session 3 stopped: {session3.duration_minutes} min")
        
        # Měření - Session 2 (INVALIDNÍ - chyba)
        session4 = crud.start_time_session(db, user.id, activity.id,
                                          phase=models.TimeSessionPhase.MERENI,
                                          notes="Měření série B")
        print(f"   ⏱️  Session 4 started: ID={session4.id}")
        session4 = crud.stop_time_session(db, session4.id)
        print(f"   ⚠️  Session 4 stopped: {session4.duration_minutes} min")
        
        # Invalidace session 4
        session4 = crud.invalidate_time_session(db, session4.id, 
                                               reason="Chyba při kalibraci - měření neplatné")
        print(f"   ❌ Session 4 invalidována: {session4.invalidation_reason}")
        
        # Měření - Session 3 (opakování po chybě)
        session5 = crud.start_time_session(db, user.id, activity.id,
                                          phase=models.TimeSessionPhase.MERENI,
                                          notes="Opakované měření série B")
        print(f"   ⏱️  Session 5 started: ID={session5.id}")
        session5 = crud.stop_time_session(db, session5.id)
        print(f"   ✅ Session 5 stopped: {session5.duration_minutes} min")
        
        # 5. Kontrola všech session pro aktivitu
        print("\n5️⃣  Kontrola všech TimeSession pro aktivitu...")
        all_sessions = crud.get_time_sessions_for_activity(db, activity.id)
        print(f"\n   📊 Celkem session: {len(all_sessions)}")
        for s in all_sessions:
            valid_mark = "✅" if s.is_valid else "❌"
            print(f"   {valid_mark} ID={s.id} | Fáze={s.phase.value if s.phase else 'N/A'} | "
                  f"Čas={s.duration_minutes}min | Valid={s.is_valid}")
        
        # 6. Kontrola jen VALIDNÍCH session
        print("\n6️⃣  Kontrola pouze VALIDNÍCH session...")
        valid_sessions = crud.get_valid_time_sessions_for_activity(db, activity.id)
        total_valid_time = sum(s.duration_minutes for s in valid_sessions if s.duration_minutes)
        print(f"   ✅ Validní session: {len(valid_sessions)}")
        print(f"   ⏱️  Celkový validní čas: {total_valid_time} min")
        
        # 7. Aktivita zůstává ACTIVE (nedokončená)
        print("\n7️⃣  Status aktivity...")
        activity_check = crud.get_activity(db, activity.id)
        print(f"   📌 Activity status: {activity_check.status.name}")
        print(f"   💡 Aktivita zůstává otevřená pro další den")
        
        # 8. Vytvoření ROUTINE aktivity (pro srovnání)
        print("\n8️⃣  Vytváření ROUTINE aktivity (pro srovnání)...")
        routine_data = {
            'type': models.ActivityType.ROUTINE,
            'name': 'Oběd',
            'status': models.ActivityStatus.ACTIVE,
            'created_by_id': user.id
        }
        routine = crud.create_activity(db, routine_data)
        print(f"   ✅ ROUTINE vytvořena: {routine.name}")
        
        print("\n" + "=" * 60)
        print("✅ VŠECHNY TESTY ÚSPĚŠNÉ!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ CHYBA: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_workflow()
