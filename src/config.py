from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_FALLBACKS = ("gemini-3.5-flash", "gemini-flash-latest")
DEFAULT_TIMEOUT = 30.0
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 512


@dataclass(frozen=True)
class ConfiguracaoLLM:
    api_key: str
    modelo_principal: str
    modelos_fallback: tuple[str, ...]
    timeout_segundos: float
    temperatura: float
    max_tokens: int


def _parse_float_positivo(nome_var: str, valor_padrao: float) -> float:
    bruto = os.getenv(nome_var, str(valor_padrao)).strip()
    try:
        valor = float(bruto)
    except ValueError as exc:
        raise ValueError(f"Configuracao invalida: {nome_var} deve ser um numero.") from exc
    if valor <= 0:
        raise ValueError(f"Configuracao invalida: {nome_var} deve ser maior que zero.")
    return valor


def _parse_int_positivo(nome_var: str, valor_padrao: int) -> int:
    bruto = os.getenv(nome_var, str(valor_padrao)).strip()
    try:
        valor = int(bruto)
    except ValueError as exc:
        raise ValueError(f"Configuracao invalida: {nome_var} deve ser um inteiro.") from exc
    if valor <= 0:
        raise ValueError(f"Configuracao invalida: {nome_var} deve ser maior que zero.")
    return valor


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
        fallbacks = tuple(m for m in DEFAULT_FALLBACKS if m != modelo_principal)
    else:
        fallbacks = tuple(
            item.strip()
            for item in raw_fallbacks.split(",")
            if item.strip() and item.strip() != modelo_principal
        )

    timeout_segundos = _parse_float_positivo("LLM_TIMEOUT_SECONDS", DEFAULT_TIMEOUT)

    temperatura_bruta = os.getenv("LLM_TEMPERATURE", str(DEFAULT_TEMPERATURE)).strip()
    try:
        temperatura = float(temperatura_bruta)
    except ValueError as exc:
        raise ValueError(
            "Configuracao invalida: LLM_TEMPERATURE deve ser um numero."
        ) from exc
    if not (0.0 <= temperatura <= 2.0):
        raise ValueError(
            "Configuracao invalida: LLM_TEMPERATURE deve estar entre 0.0 e 2.0."
        )

    max_tokens = _parse_int_positivo("LLM_MAX_TOKENS", DEFAULT_MAX_TOKENS)

    return ConfiguracaoLLM(
        api_key=api_key,
        modelo_principal=modelo_principal,
        modelos_fallback=fallbacks,
        timeout_segundos=timeout_segundos,
        temperatura=temperatura,
        max_tokens=max_tokens,
    )
