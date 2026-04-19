"""
Confirm Dialog - jednoduchý modální dialog pro potvrzení akce.

Zobrazuje zprávu a dvě tlačítka: Potvrdit / Zrušit.
Výsledek se čte přes atribut `confirmed` (bool).
"""

import customtkinter as ctk


class ConfirmDialog(ctk.CTkToplevel):
    """
    Modální potvrzovací dialog.

    Příklad použití:
        dialog = ConfirmDialog(self, title="Dokončit úkol", message="Opravdu dokončit?")
        self.wait_window(dialog)
        if dialog.confirmed:
            ...
    """

    def __init__(
        self,
        parent,
        title: str = "Potvrdit akci",
        message: str = "Opravdu chceš provést tuto akci?",
        confirm_text: str = "✅ Potvrdit",
        cancel_text: str = "❌ Zrušit",
        confirm_color: str = "green",
        confirm_hover: str = "darkgreen",
    ):
        """
        Inicializace dialogu.

        Args:
            parent: Rodičovský widget
            title: Nadpis okna
            message: Text zobrazený uživateli (podporuje víceřádkový text)
            confirm_text: Popisek potvrzovacího tlačítka
            cancel_text: Popisek tlačítka Zrušit
            confirm_color: Barva potvrzovacího tlačítka
            confirm_hover: Barva potvrzovacího tlačítka při hover
        """
        super().__init__(parent)

        self.confirmed: bool = False

        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets(message, confirm_text, cancel_text, confirm_color, confirm_hover)

        # Centrování nad rodičovským oknem
        self.update_idletasks()
        pw = parent.winfo_x() + parent.winfo_width() // 2
        ph = parent.winfo_y() + parent.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w // 2}+{ph - h // 2}")

    def _create_widgets(
        self,
        message: str,
        confirm_text: str,
        cancel_text: str,
        confirm_color: str,
        confirm_hover: str,
    ) -> None:
        """Vytvoří obsah dialogu."""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=340,
            justify="center",
        ).pack(pady=(10, 20))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_frame,
            text=cancel_text,
            command=self._on_cancel,
            height=40,
            fg_color="gray40",
            hover_color="gray50",
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            command=self._on_confirm,
            height=40,
            fg_color=confirm_color,
            hover_color=confirm_hover,
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _on_confirm(self) -> None:
        """Uživatel potvrdil akci."""
        self.confirmed = True
        self.grab_release()
        self.destroy()

    def _on_cancel(self) -> None:
        """Uživatel zrušil akci."""
        self.confirmed = False
        self.grab_release()
        self.destroy()
