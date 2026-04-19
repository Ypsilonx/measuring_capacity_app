"""
Application Logger — singleton logger pro celou aplikaci.

Poskytuje:
- FileHandler → data/app.log (rotující, max 1 MB, 3 zálohy)
- StreamHandler → konzole
- GUI dispatch handler → volá registrované callbacky pro GUI log panel

Použití:
    from src.utils.app_logger import get_logger
    logger = get_logger()
    logger.info("Zpráva")
    logger.warning("Varování")
    logger.error("Chyba")
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# --- Cesta k log souboru (stejný vzor jako database.py) ---
DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "app.log")

# Formát pro soubor a konzoli
_FILE_FORMAT = "%(asctime)s [%(levelname)-8s] %(message)s"
_DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

# Formát pro GUI panel — pouze čas a zpráva, bez level textu
_GUI_FORMAT = "%(asctime)s  %(message)s"
_GUI_DATE_FORMAT = "%H:%M:%S"

# --- Singleton instance ---
_logger: logging.Logger | None = None

# --- Registrované GUI callbacky ---
# Každý callback má signaturu: callback(message: str, level: str) -> None
_gui_callbacks: list = []


class _GUIDispatchHandler(logging.Handler):
    """
    Logging handler pro GUI.

    Při každém záznamu zavolá všechny registrované GUI callbacky
    s naformátovanou zprávou a názvem úrovně (INFO, WARNING, ERROR...).
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Předá záznam všem registrovaným GUI callbackům."""
        try:
            message = self.format(record)
            level = record.levelname
            for callback in list(_gui_callbacks):
                try:
                    callback(message, level)
                except Exception:
                    # Callback selhal — tiše ignorujeme, aby se nezastavilo logování
                    pass
        except Exception:
            self.handleError(record)


def get_logger() -> logging.Logger:
    """
    Vrátí singleton instanci aplikačního loggeru.

    Při prvním zavolání inicializuje handlery (soubor, konzole, GUI).
    Při dalších zavoláních vrátí již existující instanci.

    Returns:
        logging.Logger: Nakonfigurovaný logger "measuring_capacity"
    """
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger("measuring_capacity")
    _logger.setLevel(logging.DEBUG)

    # Zabrání duplicitnímu přidávání handlerů při opakované inicializaci
    if _logger.handlers:
        return _logger

    formatter = logging.Formatter(_FILE_FORMAT, datefmt=_DATE_FORMAT)

    # --- Konzolový handler ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    # --- Souborový handler (rotující) ---
    os.makedirs(DATA_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,   # 1 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    # --- GUI dispatch handler ---
    gui_handler = _GUIDispatchHandler()
    gui_handler.setLevel(logging.INFO)  # Do GUI posíláme jen INFO a výše
    gui_handler.setFormatter(
        logging.Formatter(_GUI_FORMAT, datefmt=_GUI_DATE_FORMAT)
    )
    _logger.addHandler(gui_handler)

    return _logger


def add_gui_handler(callback) -> None:
    """
    Zaregistruje callback pro příjem log zpráv v GUI.

    Args:
        callback: Funkce se signaturou callback(message: str, level: str)
    """
    if callback not in _gui_callbacks:
        _gui_callbacks.append(callback)


def remove_gui_handler(callback) -> None:
    """
    Odregistruje dříve zaregistrovaný GUI callback.

    Args:
        callback: Dříve zaregistrovaná funkce
    """
    if callback in _gui_callbacks:
        _gui_callbacks.remove(callback)
