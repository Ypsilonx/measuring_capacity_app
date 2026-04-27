"""
Edit Activity Dialog - dialog pro editaci existujícího PROJECT_TASK.

Umožňuje změnit metadata aktivity po jejím vytvoření:
- TMA číslo
- Název testu
- Zadavatel
- Projekt
- Obsah měření (ENUM)
- Důvod měření
- Počet kusů

Formulář je předvyplněn aktuálními hodnotami z databáze.
"""

import customtkinter as ctk
from src.database import crud, models
from src.utils.app_logger import get_logger

logger = get_logger()


class EditActivityDialog(ctk.CTkToplevel):
    """Dialog pro editaci metadat existujícího PROJECT_TASK."""

    def __init__(self, parent, planner, activity: models.Activity):
        """
        Inicializace dialogu.

        Args:
            parent: Rodičovský widget
            planner: Reference na PlannerWindow (poskytuje db session a current_user)
            activity: Activity objekt k editaci
        """
        super().__init__(parent)

        self.planner = planner
        self.db = planner.db
        self.activity = activity

        self.title(f"✏️ Editovat PROJECT_TASK — {activity.tma_cislo or f'ID={activity.id}'}")

        # Responzivní velikost
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if screen_height < 900:
            width, height = 550, min(screen_height - 100, 700)
        else:
            width, height = 700, 850

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(500, 600)

        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_lookups()

    def _create_widgets(self) -> None:
        """Vytvoří formulářové prvky a předvyplní je aktuálními hodnotami."""

        form_frame = ctk.CTkScrollableFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # === TMA číslo ===
        ctk.CTkLabel(
            form_frame,
            text="TMA číslo *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 5))

        self.tma_entry = ctk.CTkEntry(form_frame, placeholder_text="např. TMA-2025-001")
        self.tma_entry.pack(fill="x", pady=5)
        if self.activity.tma_cislo:
            self.tma_entry.insert(0, self.activity.tma_cislo)

        # === Název testu ===
        ctk.CTkLabel(
            form_frame,
            text="Název testu *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 5))

        self.test_name_entry = ctk.CTkEntry(form_frame, placeholder_text="např. Geometrie dílu X")
        self.test_name_entry.pack(fill="x", pady=5)
        if self.activity.nazev_testu:
            self.test_name_entry.insert(0, self.activity.nazev_testu)

        # === Zadavatel ===
        ctk.CTkLabel(
            form_frame,
            text="Zadavatel *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 5))

        self.zadavatel_combo = ctk.CTkComboBox(
            form_frame, values=["Načítám..."], state="readonly"
        )
        self.zadavatel_combo.pack(fill="x", pady=5)

        ctk.CTkButton(
            form_frame,
            text="+ Nový zadavatel",
            command=self._add_zadavatel,
            height=25,
            fg_color="gray40",
        ).pack(anchor="e", pady=2)

        # === Projekt ===
        ctk.CTkLabel(
            form_frame,
            text="Projekt *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 5))

        self.projekt_combo = ctk.CTkComboBox(
            form_frame, values=["Načítám..."], state="readonly"
        )
        self.projekt_combo.pack(fill="x", pady=5)

        ctk.CTkButton(
            form_frame,
            text="+ Nový projekt",
            command=self._add_projekt,
            height=25,
            fg_color="gray40",
        ).pack(anchor="e", pady=2)

        # === Obsah měření ===
        ctk.CTkLabel(
            form_frame,
            text="Obsah měření *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 5))

        self.obsah_combo = ctk.CTkComboBox(
            form_frame,
            values=["FREEPLAY", "FUNCTION", "OSTATNÍ"],
            state="readonly",
        )
        self.obsah_combo.pack(fill="x", pady=5)
        # Předvyplnit aktuální hodnotu
        if self.activity.obsah_mereni:
            self.obsah_combo.set(self.activity.obsah_mereni.value)
        else:
            self.obsah_combo.set("FUNCTION")

        # === Důvod měření ===
        ctk.CTkLabel(
            form_frame,
            text="Důvod měření",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 5))

        self.duvod_combo = ctk.CTkComboBox(
            form_frame, values=["Načítám..."], state="readonly"
        )
        self.duvod_combo.pack(fill="x", pady=5)

        ctk.CTkButton(
            form_frame,
            text="+ Nový důvod",
            command=self._add_duvod,
            height=25,
            fg_color="gray40",
        ).pack(anchor="e", pady=2)

        # === Počet kusů ===
        ctk.CTkLabel(
            form_frame,
            text="Počet kusů",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 5))

        self.pocet_ks_entry = ctk.CTkEntry(form_frame, placeholder_text="např. 10")
        self.pocet_ks_entry.pack(fill="x", pady=5)
        if self.activity.pocet_ks is not None:
            self.pocet_ks_entry.insert(0, str(self.activity.pocet_ks))

        # === Chybový label ===
        self._error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#FF5555",
            anchor="w",
            wraplength=460,
        )
        self._error_label.pack(fill="x", padx=20, pady=(0, 2))

        # === Tlačítka ===
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=10)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            button_frame,
            text="❌ Zrušit",
            command=self.destroy,
            height=50,
            fg_color="gray40",
        ).grid(row=0, column=0, padx=5, sticky="ew")

        ctk.CTkButton(
            button_frame,
            text="✅ Uložit změny",
            command=self._save,
            height=50,
            fg_color="green",
            hover_color="darkgreen",
        ).grid(row=0, column=1, padx=5, sticky="ew")

    def _load_lookups(self) -> None:
        """Načte data pro dropdowny a předvybere aktuální hodnoty aktivity."""

        # Zadavatelé
        zadavatele = crud.get_all_lookup_items(self.db, models.Zadavatel, limit=1000)
        self.zadavatel_map = {z.name: z.id for z in zadavatele}
        self.zadavatel_combo.configure(
            values=list(self.zadavatel_map.keys()) if self.zadavatel_map else ["Žádné záznamy"]
        )
        # Předvyplnit aktuálního zadavatele
        if self.activity.zadavatel and self.activity.zadavatel.name in self.zadavatel_map:
            self.zadavatel_combo.set(self.activity.zadavatel.name)
        elif self.zadavatel_map:
            self.zadavatel_combo.set(list(self.zadavatel_map.keys())[0])

        # Projekty
        projekty = crud.get_all_lookup_items(self.db, models.Projekt, limit=1000)
        self.projekt_map = {f"{p.code} - {p.name}": p.id for p in projekty}
        self.projekt_combo.configure(
            values=list(self.projekt_map.keys()) if self.projekt_map else ["Žádné záznamy"]
        )
        # Předvyplnit aktuální projekt
        if self.activity.projekt:
            current_projekt_key = f"{self.activity.projekt.code} - {self.activity.projekt.name}"
            if current_projekt_key in self.projekt_map:
                self.projekt_combo.set(current_projekt_key)
        elif self.projekt_map:
            self.projekt_combo.set(list(self.projekt_map.keys())[0])

        # Důvody měření
        duvody = crud.get_all_lookup_items(self.db, models.DuvodMereni, limit=1000)
        self.duvod_map = {d.name: d.id for d in duvody}
        self.duvod_combo.configure(
            values=list(self.duvod_map.keys()) if self.duvod_map else ["Žádné záznamy"]
        )
        # Předvyplnit aktuální důvod
        if self.activity.duvod_mereni and self.activity.duvod_mereni.name in self.duvod_map:
            self.duvod_combo.set(self.activity.duvod_mereni.name)
        elif self.duvod_map:
            self.duvod_combo.set(list(self.duvod_map.keys())[0])

    def _show_error(self, message: str, field_widget=None) -> None:
        """
        Zobrazí chybovou zprávu a volitelně zvýrazní pole.

        Args:
            message: Text chyby
            field_widget: Pole k vizuálnímu zvýraznění (volitelné)
        """
        self._error_label.configure(text=f"⚠️  {message}")
        if field_widget is not None:
            field_widget.configure(border_color="#FF5555")
            field_widget.focus_set()

    def _clear_errors(self) -> None:
        """Vymaže chybovou zprávu a obnoví výchozí styl polí."""
        self._error_label.configure(text="")
        default_border = ("#979DA2", "#565B5E")
        for widget in (self.tma_entry, self.test_name_entry, self.pocet_ks_entry):
            widget.configure(border_color=default_border)

    def _add_zadavatel(self) -> None:
        """Přidá nového zadavatele přes CTkInputDialog."""
        dialog = ctk.CTkInputDialog(text="Název zadavatele:", title="Nový zadavatel")
        name = dialog.get_input()
        if name:
            try:
                new_item = crud.create_lookup_item(self.db, models.Zadavatel, name=name, email="")
                logger.info(f"Zadavatel vytvořen: {new_item.name}")
                self._load_lookups()
                self.zadavatel_combo.set(name)
            except Exception as e:
                logger.error(f"Chyba při vytváření zadavatele: {e}")

    def _add_projekt(self) -> None:
        """Přidá nový projekt přes CTkInputDialog."""
        code_dialog = ctk.CTkInputDialog(text="Kód projektu:", title="Nový projekt")
        code = code_dialog.get_input()
        if code:
            name_dialog = ctk.CTkInputDialog(text="Název projektu:", title="Nový projekt")
            name = name_dialog.get_input()
            if name:
                try:
                    new_item = crud.create_lookup_item(self.db, models.Projekt, code=code, name=name)
                    display = f"{new_item.code} - {new_item.name}"
                    logger.info(f"Projekt vytvořen: {display}")
                    self._load_lookups()
                    self.projekt_combo.set(display)
                except Exception as e:
                    logger.error(f"Chyba při vytváření projektu: {e}")

    def _add_duvod(self) -> None:
        """Přidá nový důvod měření přes CTkInputDialog."""
        dialog = ctk.CTkInputDialog(text="Název důvodu:", title="Nový důvod měření")
        name = dialog.get_input()
        if name:
            try:
                new_item = crud.create_lookup_item(self.db, models.DuvodMereni, name=name)
                logger.info(f"Důvod měření vytvořen: {new_item.name}")
                self._load_lookups()
                self.duvod_combo.set(name)
            except Exception as e:
                logger.error(f"Chyba při vytváření důvodu měření: {e}")

    def _save(self) -> None:
        """
        Validuje formulář a uloží změny do databáze.

        Kontroluje povinná pole (TMA, název testu).
        Při duplicitním TMA (jiná aktivita se stejným číslem) zobrazí chybu.
        """
        self._clear_errors()

        tma = self.tma_entry.get().strip()
        nazev_testu = self.test_name_entry.get().strip()

        # Povinná pole
        if not tma:
            self._show_error("TMA číslo je povinné.", self.tma_entry)
            return
        if not nazev_testu:
            self._show_error("Název testu je povinný.", self.test_name_entry)
            return

        # Kontrola duplicitního TMA — jen pro jiné aktivity (ne pro tuto samotnou)
        existing = crud.get_activity_by_tma(self.db, tma)
        if existing and existing.id != self.activity.id:
            status_label = "ACTIVE" if existing.status == models.ActivityStatus.ACTIVE else "COMPLETED"
            self._show_error(
                f"TMA {tma!r} již používá jiná aktivita (ID={existing.id}, {status_label}).",
                self.tma_entry,
            )
            return

        # Počet kusů — volitelný, musí být číslo pokud zadán
        pocet_ks_raw = self.pocet_ks_entry.get().strip()
        pocet_ks = None
        if pocet_ks_raw:
            try:
                pocet_ks = int(pocet_ks_raw)
                if pocet_ks < 0:
                    raise ValueError
            except ValueError:
                self._show_error("Počet kusů musí být kladné celé číslo.", self.pocet_ks_entry)
                return

        # Lookup IDs
        zadavatel_key = self.zadavatel_combo.get()
        zadavatel_id = self.zadavatel_map.get(zadavatel_key)

        projekt_key = self.projekt_combo.get()
        projekt_id = self.projekt_map.get(projekt_key)

        # Obsah měření — mapování display hodnoty na ENUM
        obsah_map = {
            "FREEPLAY": models.ObsahMereniType.FREEPLAY,
            "FUNCTION": models.ObsahMereniType.FUNCTION,
            "OSTATNÍ": models.ObsahMereniType.OSTATNI,
        }
        obsah_mereni = obsah_map.get(self.obsah_combo.get())

        duvod_key = self.duvod_combo.get()
        duvod_id = self.duvod_map.get(duvod_key)

        # Uložení do DB
        updated = crud.update_activity(
            self.db,
            self.activity.id,
            tma_cislo=tma,
            nazev_testu=nazev_testu,
            zadavatel_id=zadavatel_id,
            projekt_id=projekt_id,
            obsah_mereni=obsah_mereni,
            duvod_mereni_id=duvod_id,
            pocet_ks=pocet_ks,
        )

        if updated:
            logger.info(
                f"Aktivita ID={self.activity.id} aktualizována: TMA={tma}, test={nazev_testu}"
            )
        else:
            logger.error(f"Nepodařilo se aktualizovat aktivitu ID={self.activity.id}")

        self.grab_release()
        self.destroy()
