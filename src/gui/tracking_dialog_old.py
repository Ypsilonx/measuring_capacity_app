"""
Tracking Dialog - dialog pro tracking času PROJECT_TASK.

Funkce:
- Výběr fáze (Příprava/Měření/Úklid)
- START tracking
- PAUZA - pozastavení s možností ROUTINE
- STOP-OK - validní ukončení
- STOP-NOK - nevalidní ukončení s důvodem
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from src.database import crud, models


class TrackingDialog(ctk.CTkToplevel):
    """Dialog pro tracking času na úkolu."""
    
    def __init__(self, parent, planner, activity):
        """
        Inicializace tracking dialogu.
        
        Args:
            parent: Rodičovský widget
            planner: Reference na PlannerWindow
            activity: Activity objekt pro tracking
        """
        super().__init__(parent)
        
        self.planner = planner
        self.activity = activity
        self.db = planner.db
        
        # Running session
        self.running_session = None
        self.is_paused = False
        self.timer_id = None
        self.paused_elapsed_seconds = 0  # Čas naběhnutý před pauzou
        
        # Nastavení okna
        self.title(f"Tracking - {activity.tma_cislo}")
        
        # Responzivní velikost - ŠIROKÝ místo dlouhého
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Pro malé obrazovky (notebook) širší a nižší okno
        if screen_height < 900:
            width, height = min(screen_width - 200, 900), 550
        else:
            # Velký monitor - ještě širší
            width, height = min(screen_width - 300, 1100), 600
        
        # Centrování
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Umožnit změnu velikosti (ale nastavit minimum)
        self.minsize(800, 500)
        self.resizable(True, True)
        
        # Modální
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._check_existing_session()
    
    def _create_widgets(self):
        """Vytvoří GUI komponenty."""
        
        # Scrollable hlavní frame
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Header - Info o úkolu ===
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        tma_label = ctk.CTkLabel(
            header_frame,
            text=f"🏷️ {self.activity.tma_cislo}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        tma_label.pack()
        
        if self.activity.nazev_testu:
            test_label = ctk.CTkLabel(
                header_frame,
                text=self.activity.nazev_testu,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                wraplength=400
            )
            test_label.pack(pady=5)
        
        # === Výběr fáze ===
        phase_frame = ctk.CTkFrame(main_frame)
        phase_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            phase_frame,
            text="Fáze:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.phase_var = ctk.StringVar(value="Měření")
        
        phases = ["Příprava", "Měření", "Úklid"]
        for phase in phases:
            radio = ctk.CTkRadioButton(
                phase_frame,
                text=phase,
                variable=self.phase_var,
                value=phase,
                font=ctk.CTkFont(size=12)
            )
            radio.pack(pady=2)
        
        # === Časovač a status ===
        self.status_frame = ctk.CTkFrame(main_frame, fg_color=("gray85", "gray25"))
        self.status_frame.pack(fill="x", pady=20)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Připraveno ke startu",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.pack(pady=5)
        
        self.timer_label = ctk.CTkLabel(
            self.status_frame,
            text="00:00:00",
            font=ctk.CTkFont(size=48, weight="bold")
        )
        self.timer_label.pack(pady=10)
        
        # === START button ===
        self.start_btn = ctk.CTkButton(
            main_frame,
            text="▶️ START",
            command=self._on_start,
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.start_btn.pack(fill="x", pady=10)
        
        # === PAUZA button (skrytý) ===
        self.pause_btn = ctk.CTkButton(
            main_frame,
            text="⏸️ PAUZA",
            command=self._on_pause,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="orange",
            hover_color="darkorange"
        )
        # Neskrývat, jen disable
        self.pause_btn.pack(fill="x", pady=5)
        self.pause_btn.configure(state="disabled")
        
        # === STOP buttons frame (skrytý) ===
        self.stop_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.stop_frame.pack(fill="x", pady=5)
        
        self.stop_frame.grid_columnconfigure(0, weight=1)
        self.stop_frame.grid_columnconfigure(1, weight=1)
        
        self.stop_ok_btn = ctk.CTkButton(
            self.stop_frame,
            text="⏹️ STOP-OK",
            command=self._on_stop_ok,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="blue",
            hover_color="darkblue",
            state="disabled"
        )
        self.stop_ok_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.stop_nok_btn = ctk.CTkButton(
            self.stop_frame,
            text="⏹️ STOP-NOK",
            command=self._on_stop_nok,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_nok_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        # === ROUTINES frame (skrytý, zobrazí se po PAUZA) ===
        self.routines_frame = ctk.CTkFrame(main_frame)
        # Nepřidávat do packu zatím
        
        ctk.CTkLabel(
            self.routines_frame,
            text="⚡ Mezitím můžete zaznamenat ROUTINE:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)
        
        # Routines buttons grid
        routines_grid = ctk.CTkFrame(self.routines_frame, fg_color="transparent")
        routines_grid.pack(fill="x", pady=5)
        
        for i in range(2):
            routines_grid.grid_columnconfigure(i, weight=1)
        
        # Zjednodušené ROUTINES tlačítka
        quick_routines = [
            {"emoji": "🍽️", "name": "Oběd", "type": models.RoutineType.OBED, "duration": 30},
            {"emoji": "☕", "name": "Káva", "type": models.RoutineType.KAVA, "duration": 10},
            {"emoji": "🚬", "name": "Kouření", "type": models.RoutineType.KOURENI, "duration": 10},
            {"emoji": "🚽", "name": "WC", "type": models.RoutineType.WC, "duration": 5},
        ]
        
        row, col = 0, 0
        for config in quick_routines:
            btn = ctk.CTkButton(
                routines_grid,
                text=f"{config['emoji']} {config['name']}\n{config['duration']}min",
                command=lambda c=config: self._quick_routine_during_pause(c),
                height=50,
                font=ctk.CTkFont(size=11)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # POKRAČOVAT button
        self.continue_btn = ctk.CTkButton(
            self.routines_frame,
            text="▶️ POKRAČOVAT v trackingu",
            command=self._on_continue,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.continue_btn.pack(fill="x", pady=10)
    
    def _check_existing_session(self):
        """Zkontroluje, zda už neběží nějaká session pro tohoto uživatele."""
        running = crud.get_running_time_session_for_user(
            self.db,
            self.planner.current_user.id
        )
        
        if running and running.activity_id == self.activity.id:
            # Pokračuj v existující session
            self.running_session = running
            self._update_ui_running()
    
    def _get_selected_phase(self):
        """Vrátí vybranou fázi jako ENUM."""
        phase_str = self.phase_var.get()
        
        if phase_str == "Příprava":
            return models.TimeSessionPhase.PRIPRAVA
        elif phase_str == "Měření":
            return models.TimeSessionPhase.MERENI
        elif phase_str == "Úklid":
            return models.TimeSessionPhase.UKLID
        
        return models.TimeSessionPhase.MERENI
    
    def _on_start(self):
        """Handler pro START tlačítko."""
        phase = self._get_selected_phase()
        
        # Start nové session
        self.running_session = crud.start_time_session(
            self.db,
            user_id=self.planner.current_user.id,
            activity_id=self.activity.id,
            phase=phase
        )
        
        print(f"⏱️  Tracking started: Phase={phase.value}")
        
        self._update_ui_running()
    
    def _update_ui_running(self):
        """Aktualizuje UI pro běžící tracking."""
        self.is_paused = False
        
        # Status
        phase_name = self.running_session.phase.value if self.running_session.phase else "N/A"
        self.status_label.configure(
            text=f"🟢 TRACKING AKTIVNÍ - {phase_name}",
            text_color="green"
        )
        
        # Buttons
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_ok_btn.configure(state="normal")
        self.stop_nok_btn.configure(state="normal")
        
        # Skryj routines frame
        self.routines_frame.pack_forget()
        
        # Start timer
        self._start_timer()
    
    def _on_pause(self):
        """Handler pro PAUZA tlačítko."""
        if not self.running_session:
            return
            
        # Vypočítej elapsed čas před pauzou
        now = datetime.utcnow()
        elapsed = now - self.running_session.start_time
        self.paused_elapsed_seconds = elapsed.total_seconds()
        
        self.is_paused = True
        
        # Stop timer
        self._stop_timer()
        
        # Status
        self.status_label.configure(
            text="⏸️ POZASTAVENO",
            text_color="orange"
        )
        
        # Zobraz ROUTINES frame
        self.routines_frame.pack(fill="x", pady=10, before=self.stop_frame)
        
        print(f"⏸️  Tracking paused at {self.paused_elapsed_seconds:.0f}s")
    
    def _on_continue(self):
        """Handler pro POKRAČOVAT tlačítko."""
        if not self.running_session:
            return
            
        # Přepočítej start_time: teď mínus elapsed čas před pauzou
        now = datetime.utcnow()
        self.running_session.start_time = now - timedelta(seconds=self.paused_elapsed_seconds)
        
        # Skryj routines frame
        self.routines_frame.pack_forget()
        
        # Obnov running UI
        self._update_ui_running()
        
        print(f"▶️  Tracking resumed from {self.paused_elapsed_seconds:.0f}s")
    
    def _quick_routine_during_pause(self, config):
        """
        Rychlé vytvoření ROUTINE během PAUZA.
        
        Args:
            config: Konfigurace ROUTINE
        """
        from src.gui.routine_dialog import RoutineDialog
        
        dialog = RoutineDialog(self, self.planner, config)
        self.wait_window(dialog)
    
    def _on_stop_ok(self):
        """Handler pro STOP-OK (validní)."""
        if not self.running_session:
            return
        
        # Stop timer
        self._stop_timer()
        
        # Ukonči session
        stopped = crud.stop_time_session(self.db, self.running_session.id)
        
        print(f"✅ Session stopped (VALID): {stopped.duration_minutes} min")
        
        # Zavři dialog
        self.grab_release()
        self.destroy()
    
    def _on_stop_nok(self):
        """Handler pro STOP-NOK (nevalidní)."""
        if not self.running_session:
            return
        
        # Stop timer
        self._stop_timer()
        
        # Dialog pro důvod
        reason_dialog = ctk.CTkInputDialog(
            text="Důvod neplatného měření:",
            title="STOP-NOK"
        )
        reason = reason_dialog.get_input()
        
        if reason is None:
            # Uživatel zrušil
            self._start_timer()  # Pokračuj
            return
        
        # Ukonči session
        stopped = crud.stop_time_session(self.db, self.running_session.id)
        
        # Invaliduj
        crud.invalidate_time_session(self.db, stopped.id, reason or "Bez udání důvodu")
        
        print(f"❌ Session stopped (INVALID): {stopped.duration_minutes} min - {reason}")
        
        # Zavři dialog
        self.grab_release()
        self.destroy()
    
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
            # Pokud není pauznuté, aktualizuj čas
            if not self.is_paused:
                # Vypočítej elapsed time
                now = datetime.utcnow()
                elapsed = now - self.running_session.start_time
                
                hours = int(elapsed.total_seconds() // 3600)
                minutes = int((elapsed.total_seconds() % 3600) // 60)
                seconds = int(elapsed.total_seconds() % 60)
                
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.timer_label.configure(text=time_str)
            
            # Schedule next update (i když je paused, abychom mohli pokračovat)
            self.timer_id = self.after(1000, self._update_timer)
    
    def destroy(self):
        """Override destroy pro cleanup."""
        self._stop_timer()
        super().destroy()
