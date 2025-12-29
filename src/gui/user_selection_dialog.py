"""
User Selection Dialog - výběr uživatele při startu aplikace.

Umožňuje:
- Výběr existujícího uživatele
- Vytvoření nového uživatele
"""

import customtkinter as ctk
from src.database.database import SessionLocal
from src.database import crud


class UserSelectionDialog(ctk.CTkToplevel):
    """Dialog pro výběr/vytvoření uživatele."""
    
    def __init__(self, parent):
        """
        Inicializace dialogu.
        
        Args:
            parent: Rodičovský widget (None pro root)
        """
        super().__init__(parent)
        
        self.selected_user = None
        self.db = SessionLocal()
        
        # Nastavení okna
        self.title("Výběr uživatele")
        self.geometry("400x500")
        
        # Centrování okna
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")
        
        # Modální dialog
        if parent:
            self.transient(parent)
        self.grab_set()
        
        # Zabránit zavření křížkem
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self._create_widgets()
        self._load_users()
    
    def _create_widgets(self):
        """Vytvoří GUI komponenty."""
        
        # Hlavní frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nadpis
        title_label = ctk.CTkLabel(
            main_frame,
            text="👤 Výběr uživatele",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Info
        info_label = ctk.CTkLabel(
            main_frame,
            text="Vyberte uživatele pro tracking času:",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(pady=(0, 20))
        
        # Seznam uživatelů
        list_label = ctk.CTkLabel(
            main_frame,
            text="Existující uživatelé:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        list_label.pack(fill="x", pady=(0, 10))
        
        # Scrollable frame pro uživatele
        self.users_frame = ctk.CTkScrollableFrame(
            main_frame,
            height=200
        )
        self.users_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Nový uživatel sekce
        separator = ctk.CTkFrame(main_frame, height=2, fg_color="gray")
        separator.pack(fill="x", pady=10)
        
        new_user_label = ctk.CTkLabel(
            main_frame,
            text="Nebo vytvořte nového:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        new_user_label.pack(fill="x", pady=(10, 5))
        
        # Formulář pro nového uživatele
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            form_frame,
            text="Uživatelské jméno:",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=10, pady=(10, 0))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="např. jan.novak"
        )
        self.username_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            form_frame,
            text="Celé jméno:",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.fullname_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="např. Jan Novák"
        )
        self.fullname_entry.pack(fill="x", padx=10, pady=(5, 10))
        
        create_btn = ctk.CTkButton(
            form_frame,
            text="➕ Vytvořit nového uživatele",
            command=self._create_new_user,
            fg_color="green",
            hover_color="darkgreen"
        )
        create_btn.pack(fill="x", padx=10, pady=(0, 10))
    
    def _load_users(self):
        """Načte seznam uživatelů."""
        
        # Vyčisti starý obsah
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        # Načti uživatele
        users = crud.get_users(self.db, limit=100)
        
        if not users:
            # Prázdný stav
            empty_label = ctk.CTkLabel(
                self.users_frame,
                text="📭 Zatím žádní uživatelé\n\nVytvořte prvního níže",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            empty_label.pack(pady=20)
            return
        
        # Vytvoř tlačítka pro každého uživatele
        for user in users:
            user_btn = ctk.CTkButton(
                self.users_frame,
                text=f"👤 {user.full_name}\n({user.username})",
                command=lambda u=user: self._select_user(u),
                height=60,
                font=ctk.CTkFont(size=14),
                anchor="center"
            )
            user_btn.pack(fill="x", pady=5, padx=5)
    
    def _select_user(self, user):
        """
        Vybere uživatele a zavře dialog.
        
        Args:
            user: User objekt
        """
        self.selected_user = user
        print(f"✅ Vybrán uživatel: {user.full_name}")
        self.db.close()
        self.grab_release()
        self.destroy()
    
    def _create_new_user(self):
        """Vytvoří nového uživatele."""
        
        username = self.username_entry.get().strip()
        fullname = self.fullname_entry.get().strip()
        
        # Validace
        if not username:
            print("❌ Uživatelské jméno je povinné")
            return
        
        if not fullname:
            print("❌ Celé jméno je povinné")
            return
        
        # Kontrola duplicity
        existing = crud.get_user_by_username(self.db, username)
        if existing:
            print(f"❌ Uživatel '{username}' již existuje")
            return
        
        try:
            # Vytvoř uživatele
            new_user = crud.create_user(self.db, username=username, full_name=fullname)
            print(f"✅ Vytvořen nový uživatel: {new_user.full_name}")
            
            # Vyčisti formulář
            self.username_entry.delete(0, 'end')
            self.fullname_entry.delete(0, 'end')
            
            # Obnov seznam
            self._load_users()
            
        except Exception as e:
            print(f"❌ Chyba při vytváření uživatele: {e}")
    
    def _on_cancel(self):
        """Handler pro pokus o zavření okna."""
        # Nelze zavřít bez výběru uživatele
        print("⚠️  Musíte vybrat nebo vytvořit uživatele!")
    
    def get_selected_user(self):
        """
        Vrátí vybraného uživatele.
        
        Returns:
            User objekt nebo None
        """
        return self.selected_user
