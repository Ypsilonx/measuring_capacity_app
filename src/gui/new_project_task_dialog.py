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
    
    def _add_zadavatel(self):
        """Přidá nového zadavatele."""
        dialog = ctk.CTkInputDialog(text="Název zadavatele:", title="Nový zadavatel")
        name = dialog.get_input()
        
        if name:
            try:
                new_item = crud.create_lookup_item(self.db, models.Zadavatel, name=name, email="")
                print(f"✅ Zadavatel vytvořen: {new_item.name}")
                self._load_lookups()
                self.zadavatel_combo.set(name)
            except Exception as e:
                print(f"❌ Chyba: {e}")
    
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
                    print(f"✅ Projekt vytvořen: {new_item.code}")
                    self._load_lookups()
                    self.projekt_combo.set(f"{code} - {name}")
                except Exception as e:
                    print(f"❌ Chyba: {e}")
    
    def _add_duvod(self):
        """Přidá nový důvod měření."""
        dialog = ctk.CTkInputDialog(text="Důvod měření:", title="Nový důvod")
        name = dialog.get_input()
        
        if name:
            try:
                new_item = crud.create_lookup_item(self.db, models.DuvodMereni, name=name)
                print(f"✅ Důvod měření vytvořen: {new_item.name}")
                self._load_lookups()
                self.duvod_combo.set(name)
            except Exception as e:
                print(f"❌ Chyba: {e}")
    
    def _save(self):
        """Uloží novou aktivitu."""
        
        # Validace povinných polí
        if not self.tma_entry.get():
            print("❌ TMA číslo je povinné")
            return
        
        if not self.test_name_entry.get():
            print("❌ Název testu je povinný")
            return
        
        # Získej ID z dropdown hodnot
        zadavatel_id = self.zadavatel_map.get(self.zadavatel_combo.get())
        projekt_id = self.projekt_map.get(self.projekt_combo.get())
        duvod_id = self.duvod_map.get(self.duvod_combo.get())
        
        # Obsah měření ENUM
        obsah_str = self.obsah_combo.get()
        if obsah_str == "FREEPLAY":
            obsah_enum = models.ObsahMereniType.FREEPLAY
        elif obsah_str == "FUNCTION":
            obsah_enum = models.ObsahMereniType.FUNCTION
        else:
            obsah_enum = models.ObsahMereniType.OSTATNI
        
        # Počet kusů
        try:
            pocet_ks = int(self.pocet_ks_entry.get()) if self.pocet_ks_entry.get() else None
        except ValueError:
            pocet_ks = None
        
        # Vytvoř aktivitu
        activity_data = {
            'type': models.ActivityType.PROJECT_TASK,
            'tma_cislo': self.tma_entry.get(),
            'nazev_testu': self.test_name_entry.get(),
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
            print(f"✅ PROJECT_TASK vytvořen: ID={new_activity.id}, TMA={new_activity.tma_cislo}")
            
            # Zavři dialog
            self.grab_release()
            self.destroy()
            
        except Exception as e:
            print(f"❌ Chyba při vytváření úkolu: {e}")
            import traceback
            traceback.print_exc()
