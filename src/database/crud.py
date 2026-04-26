# src/database/crud.py

import datetime
from datetime import timezone
from typing import Type
from sqlalchemy.orm import Session
from src.database import models
from src.database.models import Base

# --- User CRUD ---

def get_user(db: Session, user_id: int):
    """Fetches a user by their primary key (ID)."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Fetches a user by their unique username."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Fetches a list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, username: str, full_name: str):
    """Creates a new user and saves them to the database."""
    db_user = models.User(username=username, full_name=full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Generic Lookup Table Functions ---

def get_lookup_item(db: Session, model: Type[Base], item_id: int):
    """Generic function to fetch any lookup item by its ID."""
    return db.query(model).filter(model.id == item_id).first()

def get_lookup_item_by_name(db: Session, model: Type[Base], name: str):
    """Generic function to fetch any lookup item by its name."""
    return db.query(model).filter(model.name == name).first()

def get_all_lookup_items(db: Session, model: Type[Base], skip: int = 0, limit: int = 100):
    """Generic function to fetch all items from a lookup table."""
    return db.query(model).offset(skip).limit(limit).all()

def create_lookup_item(db: Session, model: Type[Base], **kwargs):
    """Generic function to create a new lookup item."""
    db_item = model(**kwargs)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# --- Activity CRUD ---

def create_activity(db: Session, activity_data: dict):
    """
    Creates a new activity (ROUTINE or PROJECT_TASK).
    'activity_data' is a dictionary with all necessary fields.
    """
    db_activity = models.Activity(**activity_data)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_activity(db: Session, activity_id: int):
    """Fetches an activity by its ID."""
    return db.query(models.Activity).filter(models.Activity.id == activity_id).first()

def get_activities(db: Session, skip: int = 0, limit: int = 100, status: models.ActivityStatus = None):
    """Fetches activities with optional filtering by status."""
    query = db.query(models.Activity)
    if status:
        query = query.filter(models.Activity.status == status)
    return query.offset(skip).limit(limit).all()

def get_activity_by_tma(db: Session, tma_cislo: str):
    """
    Vyhledá aktivitu podle TMA čísla.

    Slouží k detekci duplicit před vytvořením nového PROJECT_TASK.

    Args:
        db: Databázová session
        tma_cislo: TMA číslo k vyhledání

    Returns:
        Activity nebo None, pokud záznam neexistuje
    """
    return (
        db.query(models.Activity)
        .filter(models.Activity.tma_cislo == tma_cislo)
        .first()
    )

def update_activity_status(db: Session, activity_id: int, status: models.ActivityStatus):
    """Updates the status of an activity (e.g., to COMPLETED)."""
    db_activity = get_activity(db, activity_id)
    if db_activity:
        db_activity.status = status
        db.commit()
        db.refresh(db_activity)
    return db_activity

def reopen_activity(db: Session, activity_id: int):
    """
    Znovu otevře dokončenou aktivitu (COMPLETED → ACTIVE).

    Používá se při přeměření nebo opakování úkolu se stejným TMA číslem.

    Args:
        db: Databázová session
        activity_id: ID aktivity k opětovnému otevření

    Returns:
        Aktualizovaný Activity objekt, nebo None pokud aktivita neexistuje
    """
    return update_activity_status(db, activity_id, models.ActivityStatus.ACTIVE)

# --- TimeSession CRUD ---

def start_time_session(db: Session, user_id: int, activity_id: int, phase: models.TimeSessionPhase = None, notes: str = None):
    """Starts a new time session for a given activity and user."""
    # Optional: Check if there is another running session for this user and stop it first
    # running_session = get_running_time_session_for_user(db, user_id)
    # if running_session:
    #     stop_time_session(db, running_session.id)
    
    db_session = models.TimeSession(
        user_id=user_id,
        activity_id=activity_id,
        start_time=datetime.datetime.now(timezone.utc).replace(tzinfo=None),
        phase=phase,
        notes=notes
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def stop_time_session(db: Session, time_session_id: int):
    """Stops a running time session and calculates its duration."""
    db_session = db.query(models.TimeSession).filter(models.TimeSession.id == time_session_id).first()
    if db_session and db_session.end_time is None:
        db_session.end_time = datetime.datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Calculate duration in minutes
        duration_delta = db_session.end_time - db_session.start_time
        db_session.duration_minutes = round(duration_delta.total_seconds() / 60)
        
        db.commit()
        db.refresh(db_session)
    return db_session

def get_running_time_session_for_user(db: Session, user_id: int):
    """
    Finds the currently running time session for a specific user.
    Returns the TimeSession object or None if no session is running.
    """
    return db.query(models.TimeSession).filter(
        models.TimeSession.user_id == user_id,
        models.TimeSession.end_time == None
    ).first()

def get_time_sessions_for_activity(db: Session, activity_id: int, skip: int = 0, limit: int = 100):
    """Fetches all time sessions associated with a specific activity."""
    return db.query(models.TimeSession).filter(
        models.TimeSession.activity_id == activity_id
    ).order_by(models.TimeSession.start_time.desc()).offset(skip).limit(limit).all()

def invalidate_time_session(db: Session, time_session_id: int, reason: str):
    """Marks a time session as invalid and records the reason."""
    db_session = db.query(models.TimeSession).filter(models.TimeSession.id == time_session_id).first()
    if db_session:
        db_session.is_valid = False
        db_session.invalidation_reason = reason
        db.commit()
        db.refresh(db_session)
    return db_session

def get_valid_time_sessions_for_activity(db: Session, activity_id: int):
    """Fetches all valid time sessions for a specific activity."""
    return db.query(models.TimeSession).filter(
        models.TimeSession.activity_id == activity_id,
        models.TimeSession.is_valid == True
    ).all()


def get_today_routines(db: Session):
    """
    Vrátí všechny ROUTINE aktivity vytvořené dnes, seřazené od nejnovější.

    Používá se pro zobrazení dnešního přehledu rutin v pravém panelu PlannerWindow.

    Args:
        db: Databázová session

    Returns:
        Seznam Activity objektů (type=ROUTINE) vytvořených v dnešním dni
    """
    today_start = datetime.datetime.combine(
        datetime.date.today(), datetime.time.min
    )
    today_end = datetime.datetime.combine(
        datetime.date.today(), datetime.time.max
    )
    return (
        db.query(models.Activity)
        .filter(
            models.Activity.type == models.ActivityType.ROUTINE,
            models.Activity.created_at >= today_start,
            models.Activity.created_at <= today_end,
        )
        .order_by(models.Activity.created_at.desc())
        .all()
    )
