import logging
import os


def configurar_logger(nome: str = "p0_reescritor") -> logging.Logger:
    logger = logging.getLogger(nome)
    if logger.handlers:
        return logger

    nivel_texto = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    nivel = getattr(logging, nivel_texto, logging.INFO)
    logger.setLevel(nivel)
    logger.propagate = False

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
