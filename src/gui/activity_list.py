"""
Activity List - seznam aktivních PROJECT_TASK aktivit.

Zobrazuje:
- Všechny ACTIVE aktivity
- Informace o každé aktivitě (TMA, název testu, projekt...)
- Tlačítka: Start, Dokončit
- Celkový validní čas
"""

import customtkinter as ctk
from src.database import crud, models


class ActivityList(ctk.CTkScrollableFrame):
    """Scrollovatelný seznam aktivit."""
    
    def __init__(self, parent, main_window):
        """
        Inicializace seznamu aktivit.
        
        Args:
            parent: Rodičovský widget
            main_window: Reference na hlavní okno
        """
        super().__init__(parent, label_text="")
        
        self.main_window = main_window
        self.activity_widgets = []
        
    def refresh(self):
        """Obnoví seznam aktivit z databáze."""
        # Vyčisti staré widgety
        for widget in self.activity_widgets:
            widget.destroy()
        self.activity_widgets.clear()
        
        # Načti aktivní aktivity
        activities = crud.get_activities(
            self.main_window.db,
            status=models.ActivityStatus.ACTIVE,
            limit=100
        )
        
        # Filtruj jen PROJECT_TASK
        project_tasks = [a for a in activities if a.type == models.ActivityType.PROJECT_TASK]
        
        if not project_tasks:
            # Prázdný stav
            empty_label = ctk.CTkLabel(
                self,
                text="📭 Žádné aktivní úkoly\n\nKlikni na '➕ Nový úkol' pro vytvoření",
                font=ctk.CTkFont(size=14),
                text_color="gray",
                justify="center"
            )
            empty_label.pack(pady=50)
            self.activity_widgets.append(empty_label)
            return
        
        # Vytvoř widget pro každou aktivitu
        for activity in project_tasks:
            card = ActivityCard(self, activity, self.main_window)
            card.pack(pady=5, padx=5, fill="x")
            self.activity_widgets.append(card)


class ActivityCard(ctk.CTkFrame):
    """Karta zobrazující jednu aktivitu."""
    
    def __init__(self, parent, activity, main_window):
        """
        Inicializace karty aktivity.
        
        Args:
            parent: Rodičovský widget
            activity: Activity objekt z databáze
            main_window: Reference na hlavní okno
        """
        super().__init__(parent, fg_color=("gray85", "gray20"))
        
        self.activity = activity
        self.main_window = main_window
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Vytvoří obsah karty."""
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        
        # === Hlavička ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # TMA číslo
        tma_label = ctk.CTkLabel(
            header_frame,
            text=f"🏷️ {self.activity.tma_cislo or 'N/A'}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        tma_label.pack(anchor="w")
        
        # === Informace ===
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Název testu
        if self.activity.nazev_testu:
            test_label = ctk.CTkLabel(
                info_frame,
                text=f"📝 {self.activity.nazev_testu}",
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            test_label.pack(anchor="w", pady=2)
        
        # Projekt info
        if self.activity.projekt:
            projekt_label = ctk.CTkLabel(
                info_frame,
                text=f"📁 Projekt: {self.activity.projekt.code} - {self.activity.projekt.name}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            projekt_label.pack(anchor="w", pady=2)
        
        # Zadavatel
        if self.activity.zadavatel:
            zadavatel_label = ctk.CTkLabel(
                info_frame,
                text=f"👤 Zadavatel: {self.activity.zadavatel.name}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            zadavatel_label.pack(anchor="w", pady=2)
        
        # === Časové info ===
        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        # Spočítej celkový validní čas
        valid_sessions = crud.get_valid_time_sessions_for_activity(
            self.main_window.db,
            self.activity.id
        )
        total_time = sum(s.duration_minutes or 0 for s in valid_sessions)
        hours = total_time // 60
        minutes = total_time % 60
        
        time_label = ctk.CTkLabel(
            time_frame,
            text=f"⏱️ Celkový čas: {hours}h {minutes}min ({len(valid_sessions)} session)",
            font=ctk.CTkFont(size=11),
            text_color=("green", "lightgreen")
        )
        time_label.pack(anchor="w")
        
        # === Tlačítka ===
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # START tlačítko
        start_btn = ctk.CTkButton(
            button_frame,
            text="▶️ START",
            command=self._on_start,
            height=35,
            fg_color="green",
            hover_color="darkgreen"
        )
        start_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        # DOKONČIT tlačítko
        complete_btn = ctk.CTkButton(
            button_frame,
            text="✅ Dokončit",
            command=self._on_complete,
            height=35,
            fg_color="blue",
            hover_color="darkblue"
        )
        complete_btn.grid(row=0, column=1, padx=5, sticky="ew")
    
    def _on_start(self):
        """Handler pro tlačítko START."""
        # Získej vybranou fázi z tracking panelu
        phase = self.main_window.tracking_panel.get_selected_phase()
        
        # Spusť tracking
        self.main_window.start_tracking(self.activity.id, phase)
    
    def _on_complete(self):
        """Handler pro tlačítko DOKONČIT."""
        # Potvrzovací dialog
        dialog = ctk.CTkInputDialog(
            text=f"Opravdu dokončit úkol?\n\nTMA: {self.activity.tma_cislo}\nTest: {self.activity.nazev_testu}",
            title="Potvrzení"
        )
        
        result = dialog.get_input()
        
        if result is not None:  # Pokud uživatel potvrdil (nepřeruš)
            self.main_window.complete_activity(self.activity.id)
