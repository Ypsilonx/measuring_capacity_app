"""
Input Dialog - jednoduchý dialog pro zadání textu.
"""

import customtkinter as ctk


class InputDialog(ctk.CTkToplevel):
    """Dialog pro zadání textového vstupu."""
    
    def __init__(self, parent, title="Vstup", prompt="Zadejte hodnotu:", required=True):
        """
        Inicializace dialogu.
        
        Args:
            parent: Rodičovský widget
            title: Nadpis okna
            prompt: Text výzvy
            required: Zda je vstup povinný
        """
        super().__init__(parent)
        
        self.result = None
        self.required = required
        
        # Nastavení okna
        self.title(title)
        self.geometry("400x200")
        
        # Centrování
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 200) // 2
        self.geometry(f"+{x}+{y}")
        
        # Modální
        self.transient(parent)
        self.grab_set()
        
        # Zabránit zavření křížkem
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self._create_widgets(prompt)
    
    def _create_widgets(self, prompt):
        """Vytvoří GUI komponenty."""
        
        # Hlavní frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Prompt label
        prompt_label = ctk.CTkLabel(
            main_frame,
            text=prompt,
            font=ctk.CTkFont(size=13),
            wraplength=350
        )
        prompt_label.pack(pady=(10, 15))
        
        # Entry
        self.entry = ctk.CTkEntry(
            main_frame,
            width=350,
            height=35
        )
        self.entry.pack(pady=10)
        self.entry.focus()
        
        # Tlačítka
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=(20, 10))
        
        ok_btn = ctk.CTkButton(
            btn_frame,
            text="OK",
            command=self._on_ok,
            width=100,
            fg_color="green",
            hover_color="darkgreen"
        )
        ok_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Zrušit",
            command=self._on_cancel,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="left", padx=10)
        
        # Bind Enter key
        self.entry.bind("<Return>", lambda e: self._on_ok())
    
    def _on_ok(self):
        """Handler pro OK tlačítko."""
        value = self.entry.get().strip()
        
        if self.required and not value:
            # Pokud je povinný a prázdný, zobraz chybu
            self.entry.configure(border_color="red")
            return
        
        self.result = value if value else None
        self.grab_release()
        self.destroy()
    
    def _on_cancel(self):
        """Handler pro Zrušit tlačítko."""
        self.result = None
        self.grab_release()
        self.destroy()
    
    def get_input(self):
        """Vrátí zadaný vstup."""
        return self.result
