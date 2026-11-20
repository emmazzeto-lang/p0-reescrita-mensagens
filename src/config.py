from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_FALLBACKS = ("gemini-3.5-flash", "gemini-flash-latest")
DEFAULT_TIMEOUT = 30.0


@dataclass(frozen=True)
class ConfiguracaoLLM:
    api_key: str
    modelo_principal: str
    modelos_fallback: tuple[str, ...]
    timeout_segundos: float


def carregar_configuracao() -> ConfiguracaoLLM:
    api_key = (
        os.getenv("GEMINI_API_KEY", "").strip()
        or os.getenv("LLM_API_KEY", "").strip()
    )
    if not api_key:
        raise ValueError(
            "Credencial ausente: configure GEMINI_API_KEY no arquivo .env."
        )

    modelo_principal = (
        os.getenv("GEMINI_MODEL", "").strip()
        or os.getenv("LLM_MODEL", "").strip()
        or DEFAULT_MODEL
    )
    if not modelo_principal:
        raise ValueError("Configuracao invalida: o nome do modelo nao pode ser vazio.")

    raw_fallbacks = os.getenv("GEMINI_FALLBACK_MODELS")
    if raw_fallbacks is None:
        fallbacks = tuple(
            m for m in DEFAULT_FALLBACKS if m != modelo_principal
        )
    else:
        fallbacks = tuple(
            item.strip()
            for item in raw_fallbacks.split(",")
            if item.strip() and item.strip() != modelo_principal
        )

    raw_timeout = os.getenv("LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT)).strip()
    try:
        timeout_segundos = float(raw_timeout)
    except ValueError as exc:
        raise ValueError(
            "Configuracao invalida: LLM_TIMEOUT_SECONDS deve ser um numero."
        ) from exc

    if timeout_segundos <= 0:
        raise ValueError(
            "Configuracao invalida: LLM_TIMEOUT_SECONDS deve ser maior que zero."
        )

    return ConfiguracaoLLM(
        api_key=api_key,
        modelo_principal=modelo_principal,
        modelos_fallback=fallbacks,
        timeout_segundos=timeout_segundos,
    )
