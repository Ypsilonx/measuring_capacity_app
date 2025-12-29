"""
Hlavní okno aplikace - CustomTkinter GUI.

Obsahuje:
- Seznam aktivních aktivit (PROJECT_TASK)
- Tracking panel (Start/Stop časování)
- Formulář pro vytvoření nové aktivity
"""

import customtkinter as ctk
from datetime import datetime
from src.database.database import SessionLocal
from src.database import crud, models
from src.gui.tracking_panel import TrackingPanel
from src.gui.activity_list import ActivityList
from src.gui.new_activity_dialog import NewActivityDialog

# Nastavení CustomTkinter vzhledu
ctk.set_appearance_mode("dark")  # "dark" nebo "light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class MainWindow:
    """Hlavní okno aplikace."""
    
    def __init__(self):
        """Inicializace hlavního okna."""
        self.root = ctk.CTk()
        self.root.title("Measuring Capacity App")
        self.root.geometry("1200x700")
        
        # Databázová session
        self.db = SessionLocal()
        
        # Aktuální uživatel (zatím hardcoded, později přihlášení)
        self.current_user = self._get_or_create_user()
        
        # Aktivní běžící session
        self.running_session = None
        
        # Vytvoření GUI
        self._create_widgets()
        
        # Načtení dat
        self._load_data()
        
        # Kontrola běžící session
        self._check_running_session()
        
    def _get_or_create_user(self):
        """Získá nebo vytvoří výchozího uživatele."""
        user = crud.get_user_by_username(self.db, "admin")
        if not user:
            user = crud.create_user(self.db, username="admin", full_name="Administrator")
            print(f"✅ Vytvořen uživatel: {user.username}")
        return user
    
    def _create_widgets(self):
        """Vytvoří všechny GUI komponenty."""
        
        # Hlavní layout - 2 sloupce
        self.root.grid_columnconfigure(0, weight=2)  # Levý panel - širší
        self.root.grid_columnconfigure(1, weight=1)  # Pravý panel
        self.root.grid_rowconfigure(0, weight=1)
        
        # === LEVÝ PANEL - Seznam aktivit ===
        left_frame = ctk.CTkFrame(self.root)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Nadpis
        title_label = ctk.CTkLabel(
            left_frame, 
            text="📋 Aktivní úkoly (PROJECT_TASK)",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10, padx=10)
        
        # Tlačítko pro novou aktivitu
        new_btn = ctk.CTkButton(
            left_frame,
            text="➕ Nový úkol",
            command=self._show_new_activity_dialog,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        new_btn.pack(pady=5, padx=10, fill="x")
        
        # Seznam aktivit
        self.activity_list = ActivityList(left_frame, self)
        self.activity_list.pack(pady=10, padx=10, fill="both", expand=True)
        
        # === PRAVÝ PANEL - Tracking ===
        right_frame = ctk.CTkFrame(self.root)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Tracking panel
        self.tracking_panel = TrackingPanel(right_frame, self)
        self.tracking_panel.pack(pady=10, padx=10, fill="both", expand=True)
        
    def _load_data(self):
        """Načte data z databáze."""
        self.activity_list.refresh()
        
    def _check_running_session(self):
        """Zkontroluje, zda není nějaká session již spuštěná."""
        self.running_session = crud.get_running_time_session_for_user(
            self.db, 
            self.current_user.id
        )
        if self.running_session:
            self.tracking_panel.update_running_session(self.running_session)
    
    def _show_new_activity_dialog(self):
        """Zobrazí dialog pro vytvoření nové aktivity."""
        dialog = NewActivityDialog(self.root, self)
        self.root.wait_window(dialog)
        
        # Po zavření dialogu obnovit seznam
        self._load_data()
    
    def start_tracking(self, activity_id: int, phase: models.TimeSessionPhase):
        """
        Spustí tracking času pro danou aktivitu a fázi.
        
        Args:
            activity_id: ID aktivity
            phase: Fáze měření (Příprava/Měření/Úklid)
        """
        # Pokud už nějaká session běží, zastav ji
        if self.running_session:
            self.stop_tracking()
        
        # Start nové session
        self.running_session = crud.start_time_session(
            self.db,
            user_id=self.current_user.id,
            activity_id=activity_id,
            phase=phase
        )
        
        print(f"⏱️  Session started: Activity={activity_id}, Phase={phase.value}")
        
        # Update GUI
        self.tracking_panel.update_running_session(self.running_session)
        self.activity_list.refresh()
        
    def stop_tracking(self):
        """Zastaví aktuálně běžící tracking."""
        if self.running_session:
            stopped = crud.stop_time_session(self.db, self.running_session.id)
            print(f"✅ Session stopped: {stopped.duration_minutes} min")
            
            self.running_session = None
            
            # Update GUI
            self.tracking_panel.clear_running_session()
            self.activity_list.refresh()
    
    def complete_activity(self, activity_id: int):
        """Označí aktivitu jako dokončenou."""
        crud.update_activity_status(
            self.db, 
            activity_id, 
            models.ActivityStatus.COMPLETED
        )
        print(f"✅ Activity {activity_id} marked as COMPLETED")
        self._load_data()
    
    def run(self):
        """Spustí hlavní smyčku aplikace."""
        print("✅ Aplikace spuštěna")
        self.root.mainloop()
        
        # Cleanup při zavření
        self.db.close()
        print("👋 Aplikace ukončena")
