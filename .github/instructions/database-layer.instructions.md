---
description: "Use when adding models, CRUD functions, database queries, migrations, or new lookup tables to measuring_capacity_app. Covers SQLAlchemy patterns, session management, enum usage, and referential integrity rules."
applyTo: "src/database/**"
---
# Databázová vrstva — konvence

## Přidání nového modelu (models.py)

- Všechny modely dědí z `Base` (importován z `database.py`)
- Nové tabulky mají vždy: `id` (PK), `created_at` s `default=func.now()`
- Vztahy (relationships) definuj vždy na obou stranách (`back_populates`)
- Cizí klíče používej jako `nullable=True/False` záměrně — ne od oka
- Pro výčtové hodnoty vždy vytvoř Python `enum.Enum` třídu, pak `SQLAlchemy Enum(PythonEnum)`
- Kaskádové mazání (`cascade="all, delete-orphan"`) jen tam, kde má smysl (Activity → TimeSession ano, Lookup tabulky ne)

```python
# Správný vzor pro nový model
class NovaEntita(Base):
    __tablename__ = "nova_entita"

    id = Column(Integer, primary_key=True, index=True)
    nazev = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Vztah
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    activity = relationship("Activity", back_populates="nova_entita")
```

## Přidání CRUD funkce (crud.py)

- Všechny funkce přijímají `db: Session` jako první parametr
- Nikdy nevytvářej SessionLocal() uvnitř crud.py — session přichází zvenčí
- Konvence názvů:
  - `get_<model>(db, id)` — jeden záznam
  - `get_all_<model>s(db)` — seznam
  - `create_<model>(db, ...)` — vytvoření
  - `update_<model>_<pole>(db, id, ...)` — aktualizace
  - `delete_<model>(db, id)` — smazání

```python
# Správný vzor CRUD funkce
def create_nova_entita(db: Session, nazev: str, activity_id: int) -> NovaEntita:
    entita = NovaEntita(nazev=nazev, activity_id=activity_id)
    db.add(entita)
    db.commit()
    db.refresh(entita)
    return entita
```

- Po `db.add()` vždy `db.commit()` + `db.refresh()` pro vrácení aktualizovaného záznamu
- Při úpravách (UPDATE) vždy nejdřív `db.query(...).filter(...).first()`, pak změn atribut, pak `db.commit()`

## Session management — pravidla

- `SessionLocal()` se vytváří vždy v GUI třídě (`self.db = SessionLocal()`)
- `self.db.close()` se volá při zavření dialogu/okna
- **Nikdy** neuchovávej SQLAlchemy objekty z jedné session a nepoužívej je v jiné session
- `get_db()` generator je k dispozici, ale v GUI se zatím nepoužívá — neměň tuto praxi bez konzultace

## Lookup tabulky (Zadavatel, Projekt, DuvodMereni)

- Nové lookup tabulky používají generické funkce z `crud.py`:
  - `get_all_lookup_items(db, ModelClass)`
  - `create_lookup_item(db, ModelClass, nazev)`
- Při přidávání nové lookup tabulky přidej model do `models.py` a zaregistruj ho v `init_db()`

## Zákazy

- Nespouštěj `init_db()` v produkčním kódu jinak než z `main.py`; v testech je povoleno volat `init_db()` s in-memory SQLite (`sqlite:///:memory:`)
- Nepřidávej logiku importu/exportu dat do `crud.py` — patří do `scripts/` nebo `utils/`
- Nepoužívej raw SQL (`db.execute("SELECT ...")`) — používej ORM API
