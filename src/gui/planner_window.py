"""
Planner Window - hlavní okno s plánovačem a trackingem.

Zobrazuje:
- Nedokončené PROJECT_TASK úkoly
- Rychlé tlačítka pro ROUTINES
- Možnost vytvoření nového úkolu
"""

import customtkinter as ctk
from datetime import datetime, date
from src.database.database import SessionLocal
from src.database import crud, models
from src.gui.tracking_dialog import TrackingDialog
from src.gui.new_project_task_dialog import NewProjectTaskDialog
from src.gui.routine_dialog import RoutineDialog
from src.gui.log_panel import LogPanel
from src.utils.app_logger import get_logger

logger = get_logger()

# Nastavení CustomTkinter vzhledu
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PlannerWindow:
    """Hlavní okno plánovače."""
    
    def __init__(self, user):
        """
        Inicializace plánovače.
        
        Args:
            user: User objekt (přihlášený uživatel)
        """
        self.root = ctk.CTk()
        self.root.title("Measuring Capacity App - Plánovač")
        
        # Responzivní velikost podle obrazovky
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 85% šířky a 80% výšky obrazovky
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.80)
        
        # Minimální rozměry pro malé obrazovky
        window_width = max(window_width, 1000)
        window_height = max(window_height, 600)
        
        # Maximální rozměry pro velké obrazovky
        window_width = min(window_width, 1920)
        window_height = min(window_height, 1080)
        
        # Centrování
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 600)
        
        # Databázová session
        self.db = SessionLocal()
        
        # Aktuální uživatel
        self.current_user = user
        
        # Aktuální datum
        self.current_date = date.today()
        
        # Vytvoření GUI
        self._create_widgets()
        
        # Načtení dat
        self._load_data()
        
    def _create_widgets(self):
        """Vytvoří všechny GUI komponenty."""
        
        # Hlavní layout
        self.root.grid_columnconfigure(0, weight=4)  # Levý panel - PROJECT_TASKS (80%)
        self.root.grid_columnconfigure(1, weight=1)  # Pravý panel - ROUTINES (20%)
        self.root.grid_rowconfigure(0, weight=1)     # Hlavní obsah
        self.root.grid_rowconfigure(1, weight=0)     # Log panel (pevná výška)
        
        # === LEVÝ PANEL - Nedokončené úkoly ===
        left_frame = ctk.CTkFrame(self.root)
        left_frame.grid(row=0, column=0, padx=10, pady=(10, 4), sticky="nsew")
        
        # Header s uživatelem
        header = ctk.CTkFrame(left_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        user_label = ctk.CTkLabel(
            header,
            text=f"👤 {self.current_user.full_name}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        user_label.pack(side="left")
        
        date_label = ctk.CTkLabel(
            header,
            text=f"📅 {self.current_date.strftime('%d.%m.%Y')}",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        date_label.pack(side="right")
        
        # Nadpis
        title_label = ctk.CTkLabel(
            left_frame,
            text="📋 Nedokončené úkoly",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=10, padx=10)
        
        # Seznam nedokončených úkolů
        self.tasks_frame = ctk.CTkScrollableFrame(left_frame)
        self.tasks_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Tlačítko pro nový úkol
        new_task_btn = ctk.CTkButton(
            left_frame,
            text="➕ Nový PROJECT_TASK",
            command=self._show_new_task_dialog,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        new_task_btn.pack(pady=10, padx=10, fill="x")
        
        # === PRAVÝ PANEL - Rychlé akce ROUTINES ===
        right_frame = ctk.CTkFrame(self.root)
        right_frame.grid(row=0, column=1, padx=10, pady=(10, 4), sticky="nsew")
        
        # Nadpis
        routines_title = ctk.CTkLabel(
            right_frame,
            text="⚡ Rychlé akce - ROUTINES",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        routines_title.pack(pady=10, padx=10)
        
        # Info
        info_label = ctk.CTkLabel(
            right_frame,
            text="Klikněte na tlačítko pro zaznamenání rutinní aktivity",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(pady=5, padx=10)
        
        # Grid pro ROUTINES tlačítka
        routines_grid = ctk.CTkFrame(right_frame, fg_color="transparent")
        routines_grid.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Konfigurace gridu
        for i in range(3):
            routines_grid.grid_columnconfigure(i, weight=1)
        
        # Definice ROUTINES
        self.routines_config = [
            {"emoji": "🍽️", "name": "Oběd", "type": models.RoutineType.OBED, "duration": 30},
            {"emoji": "☕", "name": "Káva", "type": models.RoutineType.KAVA, "duration": 10},
            {"emoji": "🚬", "name": "Kouření", "type": models.RoutineType.KOURENI, "duration": 10},
            {"emoji": "🚽", "name": "WC", "type": models.RoutineType.WC, "duration": 5},
            {"emoji": "⏸️", "name": "Přestávka", "type": models.RoutineType.PRESTAVKA, "duration": 15},
            {"emoji": "👥", "name": "Meeting", "type": models.RoutineType.MEETING, "duration": 30},
            {"emoji": "📊", "name": "Porada", "type": models.RoutineType.PORADA, "duration": 60},
            {"emoji": "💻", "name": "Programování", "type": models.RoutineType.PROGRAMOVANI, "duration": 120},
            {"emoji": "✏️", "name": "Vlastní...", "type": models.RoutineType.VLASTNI, "duration": 30},
        ]
        
        # Vytvoř tlačítka v gridu - menší a kompaktnější
        row, col = 0, 0
        for config in self.routines_config:
            btn = ctk.CTkButton(
                routines_grid,
                text=f"{config['emoji']}\n{config['name']}\n{config['duration']}min",
                command=lambda c=config: self._quick_routine(c),
                height=70,
                font=ctk.CTkFont(size=11),
                fg_color=("gray75", "gray25"),
                hover_color=("gray65", "gray35")
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            col += 1
            if col > 2:
                col = 0
                row += 1

        # === LOG PANEL - spodní pruh přes celou šířku ===
        log_panel = LogPanel(
            self.root,
            fg_color=("gray85", "gray10"),
            border_width=1,
            border_color=("gray70", "gray30"),
        )
        log_panel.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="ew")
    
    def _load_data(self):
        """Načte data z databáze."""
        self._refresh_tasks()
    
    def _refresh_tasks(self):
        """Obnoví seznam nedokončených úkolů."""
        
        # Vyčisti starý obsah
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
        
        # Načti ACTIVE PROJECT_TASK aktivity
        activities = crud.get_activities(
            self.db,
            status=models.ActivityStatus.ACTIVE,
            limit=100
        )
        
        # Filtruj jen PROJECT_TASK
        project_tasks = [a for a in activities if a.type == models.ActivityType.PROJECT_TASK]
        
        if not project_tasks:
            # Prázdný stav
            empty_label = ctk.CTkLabel(
                self.tasks_frame,
                text="🎉 Žádné nedokončené úkoly!\n\nVytvořte nový pomocí tlačítka níže",
                font=ctk.CTkFont(size=14),
                text_color="gray",
                justify="center"
            )
            empty_label.pack(pady=50)
            return
        
        # Vytvoř karty pro úkoly
        for activity in project_tasks:
            card = TaskCard(self.tasks_frame, activity, self)
            card.pack(pady=5, padx=5, fill="x")
    
    def _show_new_task_dialog(self):
        """Zobrazí dialog pro vytvoření nového úkolu."""
        dialog = NewProjectTaskDialog(self.root, self)
        self.root.wait_window(dialog)
        self._refresh_tasks()
    
    def _quick_routine(self, config):
        """
        Rychlé vytvoření ROUTINE aktivity.
        
        Args:
            config: Slovník s konfigurací ROUTINE
        """
        dialog = RoutineDialog(self.root, self, config)
        self.root.wait_window(dialog)
    
    def open_tracking(self, activity):
        """
        Otevře tracking dialog pro aktivitu.
        
        Args:
            activity: Activity objekt
        """
        dialog = TrackingDialog(self.root, self, activity)
        self.root.wait_window(dialog)
        self._refresh_tasks()  # Refresh po zavření
    
    def complete_activity(self, activity_id):
        """Označí aktivitu jako dokončenou."""
        crud.update_activity_status(
            self.db,
            activity_id,
            models.ActivityStatus.COMPLETED
        )
        logger.info(f"Aktivita ID={activity_id} označena jako COMPLETED")
        self._refresh_tasks()
    
    def run(self):
        """Spustí hlavní smyčku aplikace."""
        logger.info("Plánovač spuštěn")
        self.root.mainloop()

        # Cleanup při zavření
        self.db.close()
        logger.info("Aplikace ukončena")


class TaskCard(ctk.CTkFrame):
    """Karta zobrazující jeden nedokončený úkol - s ráme čkem a rozbalovacími sessions."""
    
    def __init__(self, parent, activity, planner):
        """
        Inicializace karty.
        
        Args:
            parent: Rodičovský widget
            activity: Activity objekt
            planner: Reference na PlannerWindow
        """
        # Výraznější rámeček
        super().__init__(
            parent, 
            fg_color=("gray90", "gray15"),
            border_width=2,
            border_color=("gray60", "gray40"),
            corner_radius=8
        )
        
        self.activity = activity
        self.planner = planner
        self.sessions_expanded = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Vytvoří obsah karty."""
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        
        # TMA
        tma_label = ctk.CTkLabel(
            self,
            text=f"🏷️ {self.activity.tma_cislo or 'N/A'}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        tma_label.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 5))
        
        # Název testu
        if self.activity.nazev_testu:
            test_label = ctk.CTkLabel(
                self,
                text=f"📝 {self.activity.nazev_testu}",
                font=ctk.CTkFont(size=11),
                anchor="w",
                wraplength=350
            )
            test_label.grid(row=1, column=0, sticky="w", padx=12, pady=2)
        
        # Načti VŠECHNY sessions (i invalidní)
        all_sessions = crud.get_time_sessions_for_activity(
            self.planner.db,
            self.activity.id
        )
        
        # Spočítej jen validní čas
        valid_sessions = [s for s in all_sessions if s.is_valid]
        total_time = sum(s.duration_minutes or 0 for s in valid_sessions)
        hours = total_time // 60
        minutes = total_time % 60
        
        # Poslední fáze (z validních)
        last_phase = ""
        if valid_sessions:
            last_session = valid_sessions[-1]
            if last_session.phase:
                last_phase = f" | Poslední: {last_session.phase.value}"
        
        # Počet invalidních sessions
        invalid_count = len([s for s in all_sessions if not s.is_valid])
        invalid_text = f" ({invalid_count} invalid)" if invalid_count > 0 else ""
        
        time_label = ctk.CTkLabel(
            self,
            text=f"⏱️ Celkem: {hours}h {minutes}min ({len(valid_sessions)} sessions{invalid_text}){last_phase}",
            font=ctk.CTkFont(size=10),
            text_color=("green", "lightgreen"),
            anchor="w"
        )
        time_label.grid(row=2, column=0, sticky="w", padx=12, pady=2)
        
        # Tlačítko pro rozbalení sessions (pokud jsou nějaké)
        if all_sessions:
            self.sessions_btn = ctk.CTkButton(
                self,
                text="▼ Zobrazit sessions",
                command=self._toggle_sessions,
                height=25,
                font=ctk.CTkFont(size=10),
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray40")
            )
            self.sessions_btn.grid(row=3, column=0, sticky="w", padx=12, pady=(5, 5))
            
            # Sessions frame (skrytý)
            self.sessions_frame = ctk.CTkFrame(self, fg_color=("gray80", "gray25"))
            self.all_sessions = all_sessions  # Uložit VŠECHNY sessions
        
        # Tlačítka
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=(5, 12))
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        tracking_btn = ctk.CTkButton(
            btn_frame,
            text="🎯 Tracking",
            command=self._on_tracking,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="blue",
            hover_color="darkblue"
        )
        tracking_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        complete_btn = ctk.CTkButton(
            btn_frame,
            text="✅ Dokončit",
            command=self._on_complete,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        complete_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
    
    def _toggle_sessions(self):
        """Rozbalí/sbalí seznam sessions."""
        if self.sessions_expanded:
            # Sbal
            self.sessions_frame.grid_forget()
            self.sessions_btn.configure(text="▼ Zobrazit sessions")
            self.sessions_expanded = False
        else:
            # Rozbal
            self.sessions_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 8))
            self.sessions_btn.configure(text="▲ Skrýt sessions")
            self.sessions_expanded = True
            
            # Naplň sessions frame (pokud je prázdný)
            if not self.sessions_frame.winfo_children():
                for i, session in enumerate(self.all_sessions):
                    phase_text = session.phase.value if session.phase else "N/A"
                    duration = session.duration_minutes or 0
                    start_time = session.start_time.strftime("%H:%M") if session.start_time else "N/A"
                    
                    # Rozlišení validní/invalidní
                    if session.is_valid:
                        status_icon = "✅"
                        text_color = ("green", "lightgreen")
                    else:
                        status_icon = "❌"
                        text_color = ("red", "salmon")
                        # Přidej důvod invalidace
                        if session.invalidation_reason:
                            phase_text += f" ({session.invalidation_reason})"
                    
                    session_label = ctk.CTkLabel(
                        self.sessions_frame,
                        text=f"  {status_icon} {i+1}. {start_time} - {phase_text} - {duration} min",
                        font=ctk.CTkFont(size=9),
                        text_color=text_color,
                        anchor="w"
                    )
                    session_label.pack(anchor="w", padx=8, pady=2)
    
    def _on_tracking(self):
        """Handler pro tlačítko Tracking."""
        self.planner.open_tracking(self.activity)
    
    def _on_complete(self):
        """Handler pro tlačítko Dokončit."""
        self.planner.complete_activity(self.activity.id)
