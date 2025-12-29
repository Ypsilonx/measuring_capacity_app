"""
Measuring Capacity App - Hlavní vstupní bod aplikace.

Desktop aplikace pro tracking času nad pracovními úkoly s predikcí
na základě historických dat.
"""

import sys
import os
import customtkinter as ctk

# Přidání root adresáře do Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.database import init_db
from src.gui.user_selection_dialog import UserSelectionDialog
from src.gui.planner_window import PlannerWindow

def main():
    """Hlavní funkce aplikace."""
    print("=" * 60)
    print("Measuring Capacity App - Inicializace...")
    print("=" * 60)
    
    # Inicializace databáze
    print("\n📊 Inicializace databáze...")
    init_db()
    print("✅ Databáze připravena\n")
    
    # Vytvoř root okno (skryté)
    root = ctk.CTk()
    root.withdraw()  # Skryj hlavní okno
    
    # Zobraz user selection dialog
    print("👤 Výběr uživatele...")
    user_dialog = UserSelectionDialog(root)
    root.wait_window(user_dialog)
    
    selected_user = user_dialog.get_selected_user()
    
    if not selected_user:
        print("❌ Nebyl vybrán žádný uživatel. Aplikace se ukončuje.")
        root.destroy()
        return
    
    print(f"✅ Vybrán uživatel: {selected_user.full_name}")
    
    # Spuštění hlavní aplikace s vybraným uživatelem
    print("🚀 Spouštění plánovače...")
    root.destroy()  # Zruš skryté okno
    
    app = PlannerWindow(selected_user)
    app.run()

if __name__ == "__main__":
    main()
