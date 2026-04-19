"""
New Project Task Dialog - dialog pro vytvoření nového PROJECT_TASK.

Formulář obsahuje:
- TMA číslo
- Název testu
- Zadavatel (samostatný seznam)
- Projekt (samostatný seznam)
- Obsah měření (ENUM: FREEPLAY, FUNCTION, OSTATNÍ)
- Důvod měření
- Počet kusů
"""

import customtkinter as ctk
from src.database import crud, models
from src.utils.app_logger import get_logger

logger = get_logger()


class NewProjectTaskDialog(ctk.CTkToplevel):
    """Dialog pro vytvoření nového PROJECT_TASK."""
    
    def __init__(self, parent, planner):
        """
        Inicializace dialogu.
        
        Args:
            parent: Rodičovský widget
            planner: Reference na PlannerWindow
        """
        super().__init__(parent)
        
        self.planner = planner
        self.db = planner.db
        
        # Nastavení okna
        self.title("➕ Nový PROJECT_TASK")
        
        # Responzivní velikost
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        if screen_height < 900:
            # Malý monitor
            width, height = 550, min(screen_height - 100, 700)
        else:
            # Velký monitor
            width, height = 700, 850
        
        # Centrování
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Minimální velikost
        self.minsize(500, 600)

        # Modální
        self.transient(parent)
        self.grab_set()

        # ID aktivity navržené ke znovuotevření (nastaví _save při COMPLETED duplikátu)
        self._pending_reopen_id: int | None = None

        self._create_widgets()
        self._load_lookups()
    
    def _create_widgets(self):
        """Vytvoří formulářové prvky."""
        
        # Scrollable frame
        form_frame = ctk.CTkScrollableFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # === TMA číslo ===
        ctk.CTkLabel(
            form_frame,
            text="TMA číslo *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.tma_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="např. TMA-2025-001"
        )
        self.tma_entry.pack(fill="x", pady=5)
        
        # === Název testu ===
        ctk.CTkLabel(
            form_frame,
            text="Název testu *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.test_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="např. Geometrie dílu X"
        )
        self.test_name_entry.pack(fill="x", pady=5)
        
        # === Zadavatel ===
        ctk.CTkLabel(
            form_frame,
            text="Zadavatel *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.zadavatel_combo = ctk.CTkComboBox(
            form_frame,
            values=["Načítám..."],
            state="readonly"
        )
        self.zadavatel_combo.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            form_frame,
            text="+ Nový zadavatel",
            command=self._add_zadavatel,
            height=25,
            fg_color="gray40"
        ).pack(anchor="e", pady=2)
        
        # === Projekt ===
        ctk.CTkLabel(
            form_frame,
            text="Projekt *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.projekt_combo = ctk.CTkComboBox(
            form_frame,
            values=["Načítám..."],
            state="readonly"
        )
        self.projekt_combo.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            form_frame,
            text="+ Nový projekt",
            command=self._add_projekt,
            height=25,
            fg_color="gray40"
        ).pack(anchor="e", pady=2)
        
        # === Obsah měření (ENUM) ===
        ctk.CTkLabel(
            form_frame,
            text="Obsah měření *",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.obsah_combo = ctk.CTkComboBox(
            form_frame,
            values=["FREEPLAY", "FUNCTION", "OSTATNÍ"],
            state="readonly"
        )
        self.obsah_combo.pack(fill="x", pady=5)
        self.obsah_combo.set("FUNCTION")  # Default
        
        # === Důvod měření ===
        ctk.CTkLabel(
            form_frame,
            text="Důvod měření",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.duvod_combo = ctk.CTkComboBox(
            form_frame,
            values=["Načítám..."],
            state="readonly"
        )
        self.duvod_combo.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            form_frame,
            text="+ Nový důvod",
            command=self._add_duvod,
            height=25,
            fg_color="gray40"
        ).pack(anchor="e", pady=2)
        
        # === Počet kusů ===
        ctk.CTkLabel(
            form_frame,
            text="Počet kusů",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.pocet_ks_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="např. 10"
        )
        self.pocet_ks_entry.pack(fill="x", pady=5)
        
        # === Tlačítka ===
        # Chybový label — zobrazen pouze při selhání validace
        self._error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#FF5555",
            anchor="w",
            wraplength=460,
        )
        self._error_label.pack(fill="x", padx=20, pady=(0, 2))

        # Panel pro znovuotevření COMPLETED aktivity — výchozí skrytý
        self._reopen_panel = ctk.CTkFrame(
            self,
            fg_color=("#3a3a1a", "#2a2a0a"),
            border_width=1,
            border_color="#CCAA00",
            corner_radius=6,
        )
        # Panel se zobrazí dynamicky — zde jen vytvoříme jeho obsah
        self._reopen_info_label = ctk.CTkLabel(
            self._reopen_panel,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#FFDD55",
            anchor="w",
            wraplength=420,
            justify="left",
        )
        self._reopen_info_label.pack(fill="x", padx=10, pady=(8, 4))

        reopen_btn_frame = ctk.CTkFrame(self._reopen_panel, fg_color="transparent")
        reopen_btn_frame.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkButton(
            reopen_btn_frame,
            text="\u21a9 Znovu otevřít",
            command=self._on_reopen,
            height=34,
            fg_color="#885500",
            hover_color="#AA6600",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            reopen_btn_frame,
            text="Ponechat zavřeno",
            command=self._on_keep_closed,
            height=34,
            fg_color="gray40",
            hover_color="gray50",
            font=ctk.CTkFont(size=12),
        ).pack(side="left")

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Zrušit",
            command=self.destroy,
            height=50,
            fg_color="gray40"
        )
        cancel_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="✅ Vytvořit",
            command=self._save,
            height=50,
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.grid(row=0, column=1, padx=5, sticky="ew")
    
    def _load_lookups(self):
        """Načte data pro dropdowny."""
        
        # Zadavatelé
        zadavatele = crud.get_all_lookup_items(self.db, models.Zadavatel, limit=1000)
        self.zadavatel_map = {z.name: z.id for z in zadavatele}
        self.zadavatel_combo.configure(
            values=list(self.zadavatel_map.keys()) if self.zadavatel_map else ["Žádné záznamy"]
        )
        if self.zadavatel_map:
            self.zadavatel_combo.set(list(self.zadavatel_map.keys())[0])
        
        # Projekty
        projekty = crud.get_all_lookup_items(self.db, models.Projekt, limit=1000)
        self.projekt_map = {f"{p.code} - {p.name}": p.id for p in projekty}
        self.projekt_combo.configure(
            values=list(self.projekt_map.keys()) if self.projekt_map else ["Žádné záznamy"]
        )
        if self.projekt_map:
            self.projekt_combo.set(list(self.projekt_map.keys())[0])
        
        # Důvody měření
        duvody = crud.get_all_lookup_items(self.db, models.DuvodMereni, limit=1000)
        self.duvod_map = {d.name: d.id for d in duvody}
        self.duvod_combo.configure(
            values=list(self.duvod_map.keys()) if self.duvod_map else ["Žádné záznamy"]
        )
        if self.duvod_map:
            self.duvod_combo.set(list(self.duvod_map.keys())[0])
    
    def _show_reopen_panel(self, activity) -> None:
        """
        Zobrazí panel s možností znovuotevření dokončené aktivity.

        Args:
            activity: Dokončená Activity se stejným TMA číslem
        """
        self._pending_reopen_id = activity.id
        self._reopen_info_label.configure(
            text=(
                f"⚠️  TMA {activity.tma_cislo!r} již existuje (ID={activity.id}) "
                f"a je označeno jako COMPLETED.\n"
                f"Chceš ho znovu otevřít, nebo ponechat zavřeno a změnit TMA?"
            )
        )
        self._reopen_panel.pack(fill="x", padx=20, pady=(0, 6), before=self._error_label)

    def _hide_reopen_panel(self) -> None:
        """Skryje panel znovuotevření a vyčistí pending stav."""
        self._pending_reopen_id = None
        self._reopen_panel.pack_forget()

    def _on_reopen(self) -> None:
        """Handler tlačítka Znovu otevřít — změní status aktivity na ACTIVE."""
        if self._pending_reopen_id is None:
            return
        crud.reopen_activity(self.db, self._pending_reopen_id)
        logger.info(f"Aktivita ID={self._pending_reopen_id} znovu otevřena (COMPLETED → ACTIVE)")
        self._hide_reopen_panel()
        self.grab_release()
        self.destroy()

    def _on_keep_closed(self) -> None:
        """Handler tlačítka Ponechat zavřeno — skryje panel, uživatel může změnit TMA."""
        self._hide_reopen_panel()
        self._clear_errors()
        self.tma_entry.focus_set()

    def _show_error(self, message: str, field_widget=None) -> None:
        """
        Zobrazí chybovou zprávu včetně volitelného zvýraznění pole.

        Args:
            message: Text chyby zobrazený uživateli
            field_widget: CTkEntry nebo CTkComboBox k zvýraznění (volitelmé)
        """
        self._error_label.configure(text=f"⚠️  {message}")
        if field_widget is not None:
            field_widget.configure(border_color="#FF5555")
            field_widget.focus_set()

    def _clear_errors(self) -> None:
        """Vymaže chybovou zprávu a obnoví výchozí styl polí."""
        self._error_label.configure(text="")
        default_border = ("#979DA2", "#565B5E")  # výchozí CTk barva
        for widget in (
            self.tma_entry,
            self.test_name_entry,
            self.pocet_ks_entry,
            self.zadavatel_combo,
            self.projekt_combo,
        ):
            widget.configure(border_color=default_border)
        self._hide_reopen_panel()

    def _add_zadavatel(self):
        """Přidá nového zadavatele."""
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
    
    def _add_projekt(self):
        """Přidá nový projekt."""
        code_dialog = ctk.CTkInputDialog(text="Kód projektu:", title="Nový projekt")
        code = code_dialog.get_input()
        
        if code:
            name_dialog = ctk.CTkInputDialog(text="Název projektu:", title="Nový projekt")
            name = name_dialog.get_input()
            
            if name:
                try:
                    new_item = crud.create_lookup_item(
                        self.db,
                        models.Projekt,
                        code=code,
                        name=name
                    )
                    logger.info(f"Projekt vytvořen: {new_item.code}")
                    self._load_lookups()
                    self.projekt_combo.set(f"{code} - {name}")
                except Exception as e:
                    logger.error(f"Chyba při vytváření projektu: {e}")
    
    def _add_duvod(self):
        """Přidá nový důvod měření."""
        dialog = ctk.CTkInputDialog(text="Důvod měření:", title="Nový důvod")
        name = dialog.get_input()
        
        if name:
            try:
                new_item = crud.create_lookup_item(self.db, models.DuvodMereni, name=name)
                logger.info(f"Důvod měření vytvořen: {new_item.name}")
                self._load_lookups()
                self.duvod_combo.set(name)
            except Exception as e:
                logger.error(f"Chyba při vytváření důvodu měření: {e}")
    
    def _save(self):
        """Uloží novou aktivitu po úspěšné validaci vstupů."""

        self._clear_errors()

        # --- Validace TMA čísla ---
        tma = self.tma_entry.get().strip()
        if not tma:
            self._show_error("TMA číslo je povinné.", self.tma_entry)
            logger.warning("Validace: TMA číslo je povinné")
            return

        existing = crud.get_activity_by_tma(self.db, tma)
        if existing:
            if existing.status == models.ActivityStatus.ACTIVE:
                self._show_error(
                    f'TMA "{tma}" je aktuálně aktivní (ID={existing.id}) — nemůžeš vytvořit duplicitu.',
                    self.tma_entry,
                )
                logger.warning(f'Validace: TMA "{tma}" je již ACTIVE')
            else:
                # COMPLETED — nabínout znovuotevření
                self._show_reopen_panel(existing)
                logger.info(f'TMA "{tma}" je COMPLETED — nabízeno znovuotevření')
            return

        # --- Validace názvu testu ---
        nazev = self.test_name_entry.get().strip()
        if not nazev:
            self._show_error("Název testu je povinný.", self.test_name_entry)
            logger.warning("Validace: Název testu je povinný")
            return

        # --- Validace zadavatele ---
        zadavatel_id = self.zadavatel_map.get(self.zadavatel_combo.get())
        if zadavatel_id is None:
            self._show_error(
                "Vyberte platného zadavatele nebo přidejte nového.",
                self.zadavatel_combo,
            )
            logger.warning("Validace: zadavatel není vybrán")
            return

        # --- Validace projektu ---
        projekt_id = self.projekt_map.get(self.projekt_combo.get())
        if projekt_id is None:
            self._show_error(
                "Vyberte platný projekt nebo přidejte nový.",
                self.projekt_combo,
            )
            logger.warning("Validace: projekt není vybrán")
            return

        # --- Validace počtu kusů (nepovinné, ale musí být číslo) ---
        pocet_ks_raw = self.pocet_ks_entry.get().strip()
        pocet_ks = None
        if pocet_ks_raw:
            try:
                pocet_ks = int(pocet_ks_raw)
                if pocet_ks <= 0:
                    raise ValueError
            except ValueError:
                self._show_error(
                    "Počet kusů musí být kladné celé číslo (nebo nechte prázdné).",
                    self.pocet_ks_entry,
                )
                logger.warning(f'Validace: neplatný počet kusů "{pocet_ks_raw}"')
                return

        # --- Sestavení dat a uložení ---
        duvod_id = self.duvod_map.get(self.duvod_combo.get())

        obsah_str = self.obsah_combo.get()
        if obsah_str == "FREEPLAY":
            obsah_enum = models.ObsahMereniType.FREEPLAY
        elif obsah_str == "FUNCTION":
            obsah_enum = models.ObsahMereniType.FUNCTION
        else:
            obsah_enum = models.ObsahMereniType.OSTATNI

        activity_data = {
            'type': models.ActivityType.PROJECT_TASK,
            'tma_cislo': tma,
            'nazev_testu': nazev,
            'zadavatel_id': zadavatel_id,
            'projekt_id': projekt_id,
            'obsah_mereni': obsah_enum,
            'duvod_mereni_id': duvod_id,
            'pocet_ks': pocet_ks,
            'status': models.ActivityStatus.ACTIVE,
            'created_by_id': self.planner.current_user.id
        }

        try:
            new_activity = crud.create_activity(self.db, activity_data)
            logger.info(f"PROJECT_TASK vytvořen: ID={new_activity.id}, TMA={new_activity.tma_cislo}")
            self.grab_release()
            self.destroy()
        except Exception as e:
            logger.error(f"Chyba při vytváření úkolu: {e}")
            self._show_error(f"Chyba při ukládání: {e}")
            import traceback
            traceback.print_exc()
