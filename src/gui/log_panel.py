"""
LogPanel — read-only log panel zobrazený v dolní části hlavního okna.

Zobrazuje posledních N zpráv z aplikačního loggeru.
Automaticky se scrolluje na poslední zprávu.
Registruje se jako GUI handler při vytvoření a odregistruje při zničení.
"""

import customtkinter as ctk
from src.utils.app_logger import add_gui_handler, remove_gui_handler

# Maximální počet řádků v panelu (starší se oříznou)
_MAX_LINES = 200


class LogPanel(ctk.CTkFrame):
    """
    Read-only log panel pro zobrazení aplikačních zpráv.

    Widget zobrazuje zprávy příchozí z aplikačního loggeru (INFO a výše).
    Určen pro umístění do spodní části hlavního okna.
    """

    def __init__(self, parent, **kwargs):
        """
        Inicializace panelu.

        Args:
            parent: Rodičovský widget (typicky root okno)
            **kwargs: Předány do ctk.CTkFrame
        """
        super().__init__(parent, **kwargs)
        self._line_count = 0
        self._create_widgets()
        add_gui_handler(self._on_log_message)

    def _create_widgets(self) -> None:
        """Vytvoří vnitřní layout panelu."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Záhlaví s nadpisem
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(4, 0))

        ctk.CTkLabel(
            header_frame,
            text="📋 Přehled akcí",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        ).pack(side="left")

        # Textové pole — read-only, výška ~4 řádky (~88 px), mono font
        self._textbox = ctk.CTkTextbox(
            self,
            height=88,
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
            wrap="word",
            activate_scrollbars=True,
        )
        self._textbox.grid(row=1, column=0, sticky="ew", padx=8, pady=(2, 6))

    def _on_log_message(self, message: str, level: str) -> None:
        """
        Callback volaný loggerem při každé nové zprávě.

        Přidání do fronty hlavního vlákna přes after(0, ...) zajišťuje
        thread-safe aktualizaci Tkinter widgetu.

        Args:
            message: Naformátovaná zpráva z loggeru
            level: Název úrovně ("INFO", "WARNING", "ERROR", ...)
        """
        # after(0, ...) naplánuje volání v hlavním Tkinter vlákně
        try:
            self.after(0, lambda m=message, l=level: self._append(m, l))
        except Exception:
            pass  # Widget již neexistuje

    def _append(self, message: str, level: str) -> None:
        """
        Připojí zprávu na konec textového pole.

        Pokud je překročen _MAX_LINES, smaže první řádek.

        Args:
            message: Text zprávy
            level: Název úrovně pro vizuální rozlišení prefixem
        """
        prefix = ""
        if level == "WARNING":
            prefix = "⚠ "
        elif level in ("ERROR", "CRITICAL"):
            prefix = "✖ "

        self._textbox.configure(state="normal")

        # Ořez starých řádků
        if self._line_count >= _MAX_LINES:
            self._textbox.delete("1.0", "2.0")
        else:
            self._line_count += 1

        self._textbox.insert("end", prefix + message + "\n")
        self._textbox.configure(state="disabled")
        self._textbox.see("end")  # Auto-scroll na poslední řádek

    def destroy(self) -> None:
        """Odregistruje GUI callback před zničením widgetu."""
        remove_gui_handler(self._on_log_message)
        super().destroy()
