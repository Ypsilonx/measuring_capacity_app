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
from src.utils.app_logger import get_logger

logger = get_logger()


def main():
    """Hlavní funkce aplikace."""
    logger.info("Measuring Capacity App — spuštění")

    # Inicializace databáze
    logger.info("Inicializace databáze...")
    init_db()
    logger.info("Databáze připravena")

    # Vytvoř root okno (skryté)
    root = ctk.CTk()
    root.withdraw()  # Skryj hlavní okno

    # Zobraz user selection dialog
    logger.info("Čekání na výběr uživatele...")
    user_dialog = UserSelectionDialog(root)
    root.wait_window(user_dialog)

    selected_user = user_dialog.get_selected_user()

    if not selected_user:
        logger.warning("Nebyl vybrán žádný uživatel — aplikace se ukončuje")
        root.destroy()
        return

    logger.info(f"Přihlášen uživatel: {selected_user.full_name}")

    # Spuštění hlavní aplikace s vybraným uživatelem
    logger.info("Spouštění plánovače...")
    root.destroy()  # Zruš skryté okno

    app = PlannerWindow(selected_user)
    app.run()

if __name__ == "__main__":
    main()
