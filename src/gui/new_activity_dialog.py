"""
Dialog pro vytvoření nové PROJECT_TASK aktivity.

Formulář obsahuje:
- TMA číslo
- Název testu
- Zadavatel (dropdown/nový)
- Projekt (dropdown/nový)
- Obsah měření (dropdown/nový)
- Důvod měření (dropdown/nový)
- Počet kusů
"""

import customtkinter as ctk
from src.database import crud, models


class NewActivityDialog(ctk.CTkToplevel):
    """Dialog pro vytvoření nové aktivity."""
    
    def __init__(self, parent, main_window):
        """
        Inicializace dialogu.
        
        Args:
            parent: Rodičovský widget
            main_window: Reference na hlavní okno
        """
        super().__init__(parent)
        
        self.main_window = main_window
        self.db = main_window.db
        
        # Nastavení okna
        self.title("➕ Nový úkol (PROJECT_TASK)")
        self.geometry("600x700")
        
        # Modální dialog
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._load_lookups()
    
    def _create_widgets(self):
        """Vytvoří formulářové prvky."""
        
        # Scrollable frame pro formulář
        form_frame = ctk.CTkScrollableFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # === TMA číslo ===
        ctk.CTkLabel(
            form_frame,
            text="TMA číslo *",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.tma_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="např. TMA-12345"
        )
        self.tma_entry.pack(fill="x", pady=5)
        
        # === Název testu ===
        ctk.CTkLabel(
            form_frame,
            text="Název testu *",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.test_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="např. Geometrie dílu X"
        )
        self.test_name_entry.pack(fill="x", pady=5)
        
        # === Zadavatel ===
        ctk.CTkLabel(
            form_frame,
            text="Zadavatel *",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.zadavatel_combo = ctk.CTkComboBox(
            form_frame,
            values=["Načítám..."],
            state="readonly"
        )
        self.zadavatel_combo.pack(fill="x", pady=5)
        
        # Tlačítko pro nového zadavatele
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
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
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
        
        # === Obsah měření ===
        ctk.CTkLabel(
            form_frame,
            text="Obsah měření",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.obsah_combo = ctk.CTkComboBox(
            form_frame,
            values=["Načítám..."],
            state="readonly"
        )
        self.obsah_combo.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            form_frame,
            text="+ Nový obsah",
            command=self._add_obsah,
            height=25,
            fg_color="gray40"
        ).pack(anchor="e", pady=2)
        
        # === Důvod měření ===
        ctk.CTkLabel(
            form_frame,
            text="Důvod měření",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
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
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
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
            fg_color="gray40"
        )
        cancel_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="✅ Vytvořit",
            command=self._save,
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.grid(row=0, column=1, padx=5, sticky="ew")
    
    def _load_lookups(self):
        """Načte data pro dropdowny."""
        
        # Zadavatelé
        zadavatele = crud.get_all_lookup_items(self.db, models.Zadavatel, limit=1000)
        self.zadavatel_map = {z.name: z.id for z in zadavatele}
        self.zadavatel_combo.configure(values=list(self.zadavatel_map.keys()) if self.zadavatel_map else ["Žádné záznamy"])
        if self.zadavatel_map:
            self.zadavatel_combo.set(list(self.zadavatel_map.keys())[0])
        
        # Projekty
        projekty = crud.get_all_lookup_items(self.db, models.Projekt, limit=1000)
        self.projekt_map = {f"{p.code} - {p.name}": p.id for p in projekty}
        self.projekt_combo.configure(values=list(self.projekt_map.keys()) if self.projekt_map else ["Žádné záznamy"])
        if self.projekt_map:
            self.projekt_combo.set(list(self.projekt_map.keys())[0])
        
        # Obsah měření
        obsahy = crud.get_all_lookup_items(self.db, models.ObsahMereni, limit=1000)
        self.obsah_map = {o.name: o.id for o in obsahy}
        self.obsah_combo.configure(values=list(self.obsah_map.keys()) if self.obsah_map else ["Žádné záznamy"])
        if self.obsah_map:
            self.obsah_combo.set(list(self.obsah_map.keys())[0])
        
        # Důvody měření
        duvody = crud.get_all_lookup_items(self.db, models.DuvodMereni, limit=1000)
        self.duvod_map = {d.name: d.id for d in duvody}
        self.duvod_combo.configure(values=list(self.duvod_map.keys()) if self.duvod_map else ["Žádné záznamy"])
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
        # Jednoduchý dialog - v produkci by měl být komplexnější
        code_dialog = ctk.CTkInputDialog(text="Kód projektu:", title="Nový projekt")
        code = code_dialog.get_input()
        
        if code:
            name_dialog = ctk.CTkInputDialog(text="Název projektu:", title="Nový projekt")
            name = name_dialog.get_input()
            
            if name and self.zadavatel_map:
                try:
                    # Použij prvního zadavatele jako default
                    first_zadavatel_id = list(self.zadavatel_map.values())[0]
                    new_item = crud.create_lookup_item(
                        self.db, 
                        models.Projekt, 
                        code=code, 
                        name=name,
                        zadavatel_id=first_zadavatel_id
                    )
                    print(f"✅ Projekt vytvořen: {new_item.code}")
                    self._load_lookups()
                    self.projekt_combo.set(f"{code} - {name}")
                except Exception as e:
                    print(f"❌ Chyba: {e}")
    
    def _add_obsah(self):
        """Přidá nový obsah měření."""
        dialog = ctk.CTkInputDialog(text="Obsah měření:", title="Nový obsah")
        name = dialog.get_input()
        
        if name:
            try:
                new_item = crud.create_lookup_item(self.db, models.ObsahMereni, name=name)
                print(f"✅ Obsah měření vytvořen: {new_item.name}")
                self._load_lookups()
                self.obsah_combo.set(name)
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
        obsah_id = self.obsah_map.get(self.obsah_combo.get())
        duvod_id = self.duvod_map.get(self.duvod_combo.get())
        
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
            'obsah_mereni_id': obsah_id,
            'duvod_mereni_id': duvod_id,
            'pocet_ks': pocet_ks,
            'status': models.ActivityStatus.ACTIVE,
            'created_by_id': self.main_window.current_user.id
        }
        
        try:
            new_activity = crud.create_activity(self.db, activity_data)
            print(f"✅ Aktivita vytvořena: ID={new_activity.id}, TMA={new_activity.tma_cislo}")
            self.destroy()
        except Exception as e:
            print(f"❌ Chyba při vytváření aktivity: {e}")
