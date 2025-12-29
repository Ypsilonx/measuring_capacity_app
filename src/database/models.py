# src/database/models.py

import enum
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Boolean,
    Text,
    func
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Python enums for type safety
class ActivityType(enum.Enum):
    ROUTINE = 'ROUTINE'
    PROJECT_TASK = 'PROJECT_TASK'

class ActivityStatus(enum.Enum):
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'

class TimeSessionPhase(enum.Enum):
    PRIPRAVA = 'Příprava'
    MERENI = 'Měření'
    UKLID = 'Úklid'

class ObsahMereniType(enum.Enum):
    FREEPLAY = 'FREEPLAY'
    FUNCTION = 'FUNCTION'
    OSTATNI = 'OSTATNÍ'

class RoutineType(enum.Enum):
    OBED = 'Oběd'
    KAVA = 'Káva'
    KOURENI = 'Kouření'
    WC = 'WC'
    PRESTAVKA = 'Přestávka'
    MEETING = 'Meeting'
    PORADA = 'Porada'
    PROGRAMOVANI = 'Programování'
    VLASTNI = 'Vlastní'

# --- Main Tables ---

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    activities = relationship('Activity', back_populates='creator')
    time_sessions = relationship('TimeSession', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)
    type = Column(SQLAlchemyEnum(ActivityType), nullable=False)
    name = Column(String(200), nullable=True)  # Name for ROUTINE, null for PROJECT_TASK which is defined by its parts

    # --- PROJECT_TASK fields (nullable) ---
    zadavatel_id = Column(Integer, ForeignKey('zadavatele.id'))
    projekt_id = Column(Integer, ForeignKey('projekty.id'))
    tma_cislo = Column(String(50))
    nazev_testu = Column(String(200))
    obsah_mereni = Column(SQLAlchemyEnum(ObsahMereniType), nullable=True)  # ENUM místo FK
    pocet_ks = Column(Integer)
    duvod_mereni_id = Column(Integer, ForeignKey('duvody_mereni.id'))
    # ---
    
    # --- ROUTINE fields (nullable) ---
    routine_type = Column(SQLAlchemyEnum(RoutineType), nullable=True)
    routine_duration_minutes = Column(Integer, nullable=True)  # Plánovaná délka
    # ---

    status = Column(SQLAlchemyEnum(ActivityStatus), nullable=False, default=ActivityStatus.ACTIVE)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    creator = relationship('User', back_populates='activities')
    zadavatel = relationship('Zadavatel', back_populates='activities')
    projekt = relationship('Projekt', back_populates='activities')
    duvod_mereni = relationship('DuvodMereni', back_populates='activities')
    time_sessions = relationship('TimeSession', back_populates='activity', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Activity(id={self.id}, type='{self.type.name}', status='{self.status.name}')>"

class TimeSession(Base):
    __tablename__ = 'time_sessions'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True) # Will be calculated on session stop

    phase = Column(SQLAlchemyEnum(TimeSessionPhase), nullable=True) # Nullable for ROUTINE
    is_valid = Column(Boolean, default=True, nullable=False)
    invalidation_reason = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    activity = relationship('Activity', back_populates='time_sessions')
    user = relationship('User', back_populates='time_sessions')

    def __repr__(self):
        return f"<TimeSession(id={self.id}, activity_id={self.activity_id}, start_time='{self.start_time}')>"


# --- Lookup Tables (Číselníky) ---

class Zadavatel(Base):
    __tablename__ = 'zadavatele'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    email = Column(String(100))
    
    activities = relationship('Activity', back_populates='zadavatel')

    def __repr__(self):
        return f"<Zadavatel(id={self.id}, name='{self.name}')>"

class Projekt(Base):
    __tablename__ = 'projekty'
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200))

    activities = relationship('Activity', back_populates='projekt')

    def __repr__(self):
        return f"<Projekt(id={self.id}, code='{self.code}')>"

class DuvodMereni(Base):
    __tablename__ = 'duvody_mereni'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    
    activities = relationship('Activity', back_populates='duvod_mereni')

    def __repr__(self):
        return f"<DuvodMereni(id={self.id}, name='{self.name}')>"

class ObsahMereni(Base):
    __tablename__ = 'obsahy_mereni'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)

    activities = relationship('Activity', back_populates='obsah_mereni')

    def __repr__(self):
        return f"<ObsahMereni(id={self.id}, name='{self.name}')>"
