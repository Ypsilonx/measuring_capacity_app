"""
Tracking Panel - pravý panel pro Start/Stop tracking času.

Zobrazuje:
- Aktuálně běžící session (pokud existuje)
- Tlačítka pro Start/Stop
- Výběr fáze (Příprava/Měření/Úklid)
- Živý časovač
"""

import customtkinter as ctk
from datetime import datetime
from src.database import models


class TrackingPanel(ctk.CTkFrame):
    """Panel pro tracking času."""
    
    def __init__(self, parent, main_window):
        """
        Inicializace tracking panelu.
        
        Args:
            parent: Rodičovský widget
            main_window: Reference na hlavní okno (MainWindow)
        """
        super().__init__(parent)
        
        self.main_window = main_window
        self.running_session = None
        self.timer_id = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Vytvoří GUI komponenty."""
        
        # Nadpis
        title = ctk.CTkLabel(
            self,
            text="⏱️ Tracking času",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # === Status panel ===
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(pady=10, padx=10, fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Žádný tracking",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.pack(pady=5)
        
        # Časovač
        self.timer_label = ctk.CTkLabel(
            self.status_frame,
            text="00:00:00",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.timer_label.pack(pady=10)
        
        # Info o aktivitě
        self.activity_info_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=250
        )
        self.activity_info_label.pack(pady=5)
        
        # === Fáze selection ===
        phase_frame = ctk.CTkFrame(self)
        phase_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(
            phase_frame,
            text="Fáze:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)
        
        self.phase_var = ctk.StringVar(value="Měření")
        
        phases = ["Příprava", "Měření", "Úklid"]
        for phase in phases:
            radio = ctk.CTkRadioButton(
                phase_frame,
                text=phase,
                variable=self.phase_var,
                value=phase
            )
            radio.pack(pady=2)
        
        # === Stop button ===
        self.stop_btn = ctk.CTkButton(
            self,
            text="⏹️ STOP",
            command=self._on_stop,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_btn.pack(pady=10, padx=10, fill="x")
        
        # Info text
        info_label = ctk.CTkLabel(
            self,
            text="💡 Start tracking:\nVyber úkol ze seznamu vlevo",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="center"
        )
        info_label.pack(pady=20)
    
    def update_running_session(self, session):
        """
        Aktualizuje panel s běžící session.
        
        Args:
            session: TimeSession objekt
        """
        self.running_session = session
        
        # Načti info o aktivitě
        activity = self.main_window.db.query(models.Activity).filter(
            models.Activity.id == session.activity_id
        ).first()
        
        # Update status
        self.status_label.configure(
            text="🟢 TRACKING AKTIVNÍ",
            text_color="green"
        )
        
        # Update info
        if activity:
            info_text = f"TMA: {activity.tma_cislo}\n"
            info_text += f"Test: {activity.nazev_testu}\n"
            info_text += f"Fáze: {session.phase.value if session.phase else 'N/A'}"
            self.activity_info_label.configure(text=info_text)
        
        # Enable stop button
        self.stop_btn.configure(state="normal")
        
        # Start timer
        self._start_timer()
    
    def clear_running_session(self):
        """Vyčistí panel po zastavení trackingu."""
        self.running_session = None
        
        # Stop timer
        self._stop_timer()
        
        # Reset status
        self.status_label.configure(
            text="Tracking zastaven",
            text_color="gray"
        )
        self.timer_label.configure(text="00:00:00")
        self.activity_info_label.configure(text="")
        
        # Disable stop button
        self.stop_btn.configure(state="disabled")
    
    def _start_timer(self):
        """Spustí živý časovač."""
        self._update_timer()
    
    def _stop_timer(self):
        """Zastaví časovač."""
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
    
    def _update_timer(self):
        """Aktualizuje zobrazení času."""
        if self.running_session:
            # Vypočítej elapsed time
            now = datetime.utcnow()
            elapsed = now - self.running_session.start_time
            
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            seconds = int(elapsed.total_seconds() % 60)
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.configure(text=time_str)
            
            # Schedule next update
            self.timer_id = self.after(1000, self._update_timer)
    
    def _on_stop(self):
        """Handler pro tlačítko STOP."""
        self.main_window.stop_tracking()
    
    def get_selected_phase(self) -> models.TimeSessionPhase:
        """
        Vrátí aktuálně vybranou fázi.
        
        Returns:
            TimeSessionPhase enum
        """
        phase_str = self.phase_var.get()
        
        if phase_str == "Příprava":
            return models.TimeSessionPhase.PRIPRAVA
        elif phase_str == "Měření":
            return models.TimeSessionPhase.MERENI
        elif phase_str == "Úklid":
            return models.TimeSessionPhase.UKLID
        
        return models.TimeSessionPhase.MERENI  # default
