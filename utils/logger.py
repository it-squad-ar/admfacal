import os
import logging
from datetime import datetime

# Ruta base para los logs
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class CustomLogFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname
        code = getattr(record, 'code', 'N/A')
        message_id = getattr(record, 'message_id', 'N/A')
        process_name = getattr(record, 'process_name', 'N/A')
        message = record.getMessage()

        return f"{timestamp} | {level} | {code} | {message_id} | {process_name} | {message}"

def setup_logger():
    """
    Configura el logger para el día actual.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{today_str}.log")

    logger = logging.getLogger("custom_logger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        formatter = CustomLogFormatter()
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def log_entry(message_id, process_name, level, code, message):
    """
    Escribe una entrada de log con los campos requeridos.

    Parámetros:
        message_id (str): ID de la entidad o evento
        process_name (str): Nombre del proceso que genera el log
        level (str): 'SUCCESS', 'WARNING', 'FATAL'
        code (str): Código del evento o error
        message (str): Descripción del log
    """
    logger = setup_logger()

    # Extra metadata para usar en el formatter
    extra = {
        "message_id": message_id,
        "process_name": process_name,
        "code": code
    }

    level = level.upper()
    if level == "SUCCESS":
        logger.info(message, extra=extra)
    elif level == "WARNING":
        logger.warning(message, extra=extra)
    elif level == "FATAL":
        logger.error(message, extra=extra)
    else:
        logger.debug(f"Nivel de log desconocido: {level}", extra=extra)
