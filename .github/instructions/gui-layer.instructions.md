---
description: "Use when creating or modifying GUI dialogs, windows, panels, or widgets in measuring_capacity_app. Covers CustomTkinter patterns, layout conventions, session management in GUI, and dialog structure."
applyTo: "src/gui/**"
---
# GUI vrstva — konvence (CustomTkinter)

## Struktura každé GUI třídy

```python
class NovyDialog(ctk.CTkToplevel):
    """Popis co dialog dělá."""

    def __init__(self, parent, db: Session, user, ...):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.result = None          # výsledek dialogu (pro modální dialogy)

        self.title("Název okna")
        self._setup_window()        # geometrie, transient, grab
        self._create_widgets()      # tvorba všech widgetů

    def _setup_window(self):
        """Nastavení okna — velikost, pozice, modalita."""
        self.geometry("800x600")
        self.transient(self.master)
        self.grab_set()

    def _create_widgets(self):
        """Tvorba a rozmístění všech widgetů."""
        ...

    def _on_confirm(self):
        """Callback pro potvrzení akce."""
        ...

    def _on_cancel(self):
        """Callback pro zrušení."""
        self.destroy()
```

## Pravidla

- Každý dialog/okno = vlastní soubor v `src/gui/`
- Jméno souboru odpovídá názvu třídy: `TrackingDialog` → `tracking_dialog.py`
- `_create_widgets()` je vždy oddělená metoda — nikdy nevkládej tvorbu widgetů do `__init__`
- Všechny callbacky jsou privátní metody (`_on_<akce>`)

## Layout

- Komplexní layouts: `grid()` s `sticky`, `padx/pady`
- Jednoduché vertikální stopy: `pack(fill="x", padx=10, pady=5)`
- Nemíchej `grid()` a `pack()` v rámci jednoho rodiče
- Pro dynamické přizpůsobení velikosti používej `winfo_screenwidth()` / `winfo_screenheight()`

```python
# Responsivní výška
screen_h = self.winfo_screenheight()
self.geometry(f"900x{int(screen_h * 0.8)}")
```

## Přístup k databázi z GUI

- Session se vytváří v `__init__`: `self.db = SessionLocal()`
- Session se zavírá v `_on_close()` nebo `destroy()`: `self.db.close()`
- **Nikdy** nevolej `db.query()` nebo `db.add()` přímo v GUI — vždy deleguj na funkci v `crud.py`

```python
# Správně
users = crud.get_users(self.db)

# Špatně — SQL logika v GUI
users = self.db.query(User).all()
```

## Modální dialogy

- Modální dialog = `transient(parent)` + `grab_set()` + `wait_window()`
- Výsledek se předává přes `self.result` atribut
- Zavolající kód čte výsledek po `wait_window()`:

```python
dialog = NovyDialog(self, self.db, self.user)
self.wait_window(dialog)
if dialog.result:
    self._refresh_data()
```

## Timer a asynchronní aktualizace

- Pro živé časovače používej `self.after(100, self._update_timer)` — nikdy `time.sleep()`
- Při zavření okna/dialogu zruš všechny naplánované `after` callbacky:

```python
def _on_close(self):
    if hasattr(self, "_timer_id"):
        self.after_cancel(self._timer_id)
    self.db.close()
    self.destroy()
```

## Formátování času

- Zobrazení doby trvání: `HH:MM:SS` formát pro živý časovač
- Zobrazení celkového času v kartách aktivit: `H:MM` (hodiny:minuty)
- Minuty ze session: vždy jako `duration_minutes` (float → int zaokrouhlení)

## Komunikace mezi dialogy a rodiči

Stav a výsledky se předávají výhradně přes konstruktor a `self.result` — nikdy přes globální proměnné.

### Dialog → rodič (výsledek po zavření)
```python
# Dialog nastaví výsledek před destroy()
def _on_confirm(self):
    self.result = self._get_form_data()
    self.destroy()

# Rodič čte výsledek po wait_window()
dialog = NovyDialog(self, self.db, self.user)
self.wait_window(dialog)
if dialog.result:
    self._refresh_data()   # nebo jiná reakce
```

### Rodič → dialog (předání kontextu)
- Všechna data, která dialog potřebuje, dostane v `__init__` jako parametry
- Dialog nikdy nenačítá data, která mu rodič mohl předat přímo

```python
# Správně — rodič předá aktivitu
dialog = TrackingDialog(self, self.db, self.user, activity=self.selected_activity)

# Špatně — dialog si načte aktivitu sám
dialog = TrackingDialog(self, self.db, self.user, activity_id=123)
# a pak uvnitř: self.activity = crud.get_activity(self.db, activity_id)
# (přijatelné pouze pokud rodič ID nezná dopředu)
```

### Refresh po akci
- Po zavření dialogu rodič vždy zavolá `_refresh_data()` nebo ekvivalent — nespoléhej na to, že dialog upraví GUI rodiče přímo
- Dialog nemá přístup k widgetům rodiče

## Zákazy

- Nepiš SQL dotazy do GUI souborů
- Netvoř SessionLocal() mimo `__init__` GUI třídy
- Nepřidávej byznys logiku (výpočty, validace) do callbacků — extrahuj je do `core/` nebo `utils/`
- Nepoužívej globální proměnné pro sdílení stavu mezi okny — předávej přes parametry konstruktoru
- Nikdy nevolej metody rodiče přímo z dialogu — rodič reaguje na `dialog.result` po `wait_window()`
