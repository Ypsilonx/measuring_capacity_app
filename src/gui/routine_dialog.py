"""
Routine Dialog - dialog pro vytvoření/editaci ROUTINE aktivity.

Umožňuje:
- Rychlé vytvoření ROUTINE s předvoleným časem
- Editace trvání aktivity
- Vlastní ROUTINE s názvem
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from src.database import crud, models
from src.utils.app_logger import get_logger

logger = get_logger()


class RoutineDialog(ctk.CTkToplevel):
    """Dialog pro ROUTINE aktivitu."""
    
    def __init__(self, parent, planner, config):
        """
        Inicializace dialogu.
        
        Args:
            parent: Rodičovský widget
            planner: Reference na PlannerWindow
            config: Slovník s konfigurací ROUTINE (emoji, name, type, duration)
        """
        super().__init__(parent)
        
        self.planner = planner
        self.config = config
        self.db = planner.db
        
        # Nastavení okna
        self.title(f"ROUTINE - {config['name']}")
        
        # Responzivní velikost
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        if screen_height < 900:
            width, height = 400, 350
        else:
            width, height = 500, 450
        
        # Centrování
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Minimální velikost
        self.minsize(380, 330)
        
        # Modální
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Vytvoří GUI komponenty."""
        
        # Hlavní frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Emoji + název
        header = ctk.CTkLabel(
            main_frame,
            text=f"{self.config['emoji']} {self.config['name']}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=(10, 20))
        
        # Info
        info_label = ctk.CTkLabel(
            main_frame,
            text="Nastavte trvání aktivity:",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(pady=5)
        
        # === Trvání ===
        duration_frame = ctk.CTkFrame(main_frame)
        duration_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(
            duration_frame,
            text="Trvání (minuty):",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        # Entry pro trvání
        self.duration_entry = ctk.CTkEntry(
            duration_frame,
            font=ctk.CTkFont(size=18),
            justify="center",
            width=100
        )
        self.duration_entry.pack(pady=10)
        self.duration_entry.insert(0, str(self.config['duration']))
        self.duration_entry.focus()
        
        # Rychlé preset buttony
        preset_frame = ctk.CTkFrame(duration_frame, fg_color="transparent")
        preset_frame.pack(pady=10)
        
        presets = [5, 10, 15, 30, 60, 120]
        for preset in presets:
            btn = ctk.CTkButton(
                preset_frame,
                text=f"{preset}",
                command=lambda p=preset: self._set_duration(p),
                width=50,
                height=30,
                font=ctk.CTkFont(size=11)
            )
            btn.pack(side="left", padx=2)
        
        # === Vlastní název (jen pro VLASTNÍ) ===
        if self.config['type'] == models.RoutineType.VLASTNI:
            custom_frame = ctk.CTkFrame(main_frame)
            custom_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                custom_frame,
                text="Název aktivity:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(pady=(10, 5))
            
            self.custom_name_entry = ctk.CTkEntry(
                custom_frame,
                placeholder_text="např. Schůzka s klientem"
            )
            self.custom_name_entry.pack(fill="x", padx=10, pady=(0, 10))
        else:
            self.custom_name_entry = None
        
        # === Tlačítka ===
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Zrušit",
            command=self.destroy,
            height=50,
            fg_color="gray40"
        )
        cancel_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="✅ Uložit",
            command=self._save,
            height=50,
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.grid(row=0, column=1, padx=5, sticky="ew")
    
    def _set_duration(self, minutes):
        """
        Nastaví trvání.
        
        Args:
            minutes: Počet minut
        """
        self.duration_entry.delete(0, 'end')
        self.duration_entry.insert(0, str(minutes))
    
    def _save(self):
        """Uloží ROUTINE aktivitu."""
        
        # Validace trvání
        try:
            duration = int(self.duration_entry.get())
            if duration <= 0:
                logger.warning("Trvání musí být kladné číslo")
                return
        except ValueError:
            logger.warning("Zadejte platné číslo minut")
            return
        
        # Název (pro VLASTNÍ)
        routine_name = None
        if self.config['type'] == models.RoutineType.VLASTNI:
            if self.custom_name_entry:
                routine_name = self.custom_name_entry.get().strip()
                if not routine_name:
                    logger.warning("Zadejte název vlastní aktivity")
                    return
        
        # Vytvoř ROUTINE aktivitu
        activity_data = {
            'type': models.ActivityType.ROUTINE,
            'name': routine_name or self.config['name'],
            'routine_type': self.config['type'],
            'routine_duration_minutes': duration,
            'status': models.ActivityStatus.COMPLETED,  # ROUTINE je hned dokončená
            'created_by_id': self.planner.current_user.id
        }
        
        try:
            activity = crud.create_activity(self.db, activity_data)
            
            # Vytvoř TimeSession pro ROUTINE (už uzavřenou)
            now = datetime.utcnow()
            start_time = now - timedelta(minutes=duration)
            
            session = crud.start_time_session(
                self.db,
                user_id=self.planner.current_user.id,
                activity_id=activity.id,
                phase=None,  # ROUTINE nemá fáze
                notes=f"ROUTINE: {activity.name}"
            )
            
            # Hned ukonči
            session.end_time = now
            session.duration_minutes = duration
            self.db.commit()
            
            logger.info(f"ROUTINE vytvořena: {activity.name} ({duration} min)")
            
            # Zavři dialog
            self.grab_release()
            self.destroy()
            
        except Exception as e:
            logger.error(f"Chyba při vytváření ROUTINE: {e}")
            import traceback
            traceback.print_exc()
