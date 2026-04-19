"""
Testy pro src/database/crud.py.

Používají in-memory SQLite databázi — žádné soubory, žádná závislost na GUI.
Každý test dostane čistou DB přes fixture `db`.

Spuštění:
    pytest tests/test_crud.py -v
"""

import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Přidání root adresáře do path (stejný vzor jako main.py)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.models import Base, ActivityType, ActivityStatus, TimeSessionPhase
from src.database import crud


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db():
    """
    Poskytne čistou in-memory SQLite session pro každý test.

    Po skončení testu session i engine zavře.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def user(db):
    """Vytvoří testovacího uživatele."""
    return crud.create_user(db, username="test.user", full_name="Test User")


@pytest.fixture
def project_task(db, user):
    """Vytvoří testovací PROJECT_TASK aktivitu."""
    return crud.create_activity(db, {
        "type": ActivityType.PROJECT_TASK,
        "tma_cislo": "TMA-2026-001",
        "nazev_testu": "Testovací měření",
        "status": ActivityStatus.ACTIVE,
        "created_by_id": user.id,
    })


# ---------------------------------------------------------------------------
# User testy
# ---------------------------------------------------------------------------

class TestCreateUser:
    def test_vytvorit_uzivatele(self, db):
        user = crud.create_user(db, username="jan.novak", full_name="Jan Novák")
        assert user.id is not None
        assert user.username == "jan.novak"
        assert user.full_name == "Jan Novák"

    def test_ziskat_uzivatele_podle_id(self, db):
        user = crud.create_user(db, username="jan.novak", full_name="Jan Novák")
        found = crud.get_user(db, user.id)
        assert found is not None
        assert found.id == user.id

    def test_ziskat_uzivatele_podle_username(self, db):
        crud.create_user(db, username="jan.novak", full_name="Jan Novák")
        found = crud.get_user_by_username(db, "jan.novak")
        assert found is not None
        assert found.username == "jan.novak"

    def test_neexistujici_uzivatel_vrati_none(self, db):
        assert crud.get_user(db, 999) is None

    def test_seznam_uzivatelu(self, db):
        crud.create_user(db, username="user1", full_name="User One")
        crud.create_user(db, username="user2", full_name="User Two")
        users = crud.get_users(db)
        assert len(users) == 2


# ---------------------------------------------------------------------------
# Activity testy
# ---------------------------------------------------------------------------

class TestCreateActivity:
    def test_vytvorit_project_task(self, db, user):
        activity = crud.create_activity(db, {
            "type": ActivityType.PROJECT_TASK,
            "tma_cislo": "TMA-2026-001",
            "nazev_testu": "Test XYZ",
            "status": ActivityStatus.ACTIVE,
            "created_by_id": user.id,
        })
        assert activity.id is not None
        assert activity.tma_cislo == "TMA-2026-001"
        assert activity.status == ActivityStatus.ACTIVE

    def test_get_activity_by_tma_existuje(self, db, project_task):
        found = crud.get_activity_by_tma(db, "TMA-2026-001")
        assert found is not None
        assert found.id == project_task.id

    def test_get_activity_by_tma_neexistuje(self, db):
        assert crud.get_activity_by_tma(db, "TMA-NEEXISTUJE") is None

    def test_seznam_aktivit_filtr_status(self, db, user):
        crud.create_activity(db, {
            "type": ActivityType.PROJECT_TASK,
            "tma_cislo": "TMA-A",
            "status": ActivityStatus.ACTIVE,
            "created_by_id": user.id,
        })
        crud.create_activity(db, {
            "type": ActivityType.PROJECT_TASK,
            "tma_cislo": "TMA-B",
            "status": ActivityStatus.COMPLETED,
            "created_by_id": user.id,
        })
        active = crud.get_activities(db, status=ActivityStatus.ACTIVE)
        assert len(active) == 1
        assert active[0].tma_cislo == "TMA-A"

    def test_update_activity_status(self, db, project_task):
        updated = crud.update_activity_status(db, project_task.id, ActivityStatus.COMPLETED)
        assert updated.status == ActivityStatus.COMPLETED

    def test_reopen_activity(self, db, project_task):
        # Nejprve dokončit
        crud.update_activity_status(db, project_task.id, ActivityStatus.COMPLETED)
        # Pak znovu otevřít
        reopened = crud.reopen_activity(db, project_task.id)
        assert reopened.status == ActivityStatus.ACTIVE

    def test_reopen_neexistujici_aktivita(self, db):
        result = crud.reopen_activity(db, 999)
        assert result is None


# ---------------------------------------------------------------------------
# TimeSession testy
# ---------------------------------------------------------------------------

class TestTimeSession:
    def test_start_session(self, db, user, project_task):
        session = crud.start_time_session(
            db,
            user_id=user.id,
            activity_id=project_task.id,
            phase=TimeSessionPhase.PRIPRAVA,
        )
        assert session.id is not None
        assert session.start_time is not None
        assert session.end_time is None
        assert session.is_valid is True

    def test_stop_session(self, db, user, project_task):
        session = crud.start_time_session(
            db,
            user_id=user.id,
            activity_id=project_task.id,
            phase=TimeSessionPhase.MERENI,
        )
        stopped = crud.stop_time_session(db, session.id)
        assert stopped.end_time is not None
        assert stopped.duration_minutes is not None
        assert stopped.duration_minutes >= 0

    def test_invalidate_session(self, db, user, project_task):
        session = crud.start_time_session(
            db,
            user_id=user.id,
            activity_id=project_task.id,
            phase=TimeSessionPhase.UKLID,
        )
        crud.stop_time_session(db, session.id)
        invalidated = crud.invalidate_time_session(db, session.id, "Testovací důvod")
        assert invalidated.is_valid is False
        assert invalidated.invalidation_reason == "Testovací důvod"

    def test_get_sessions_pro_aktivitu(self, db, user, project_task):
        crud.start_time_session(db, user_id=user.id, activity_id=project_task.id)
        crud.start_time_session(db, user_id=user.id, activity_id=project_task.id)
        sessions = crud.get_time_sessions_for_activity(db, project_task.id)
        assert len(sessions) == 2
