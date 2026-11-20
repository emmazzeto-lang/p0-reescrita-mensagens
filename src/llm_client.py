import time
import httpx
from src.config import ConfiguracaoLLM
from src.logger import configurar_logger
from src.prompt_builder import montar_payload_gemini

logger = configurar_logger()


def montar_url_modelo(modelo: str) -> str:
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent"
    )


def enviar_requisicao_modelo(
    prompt: str, config: ConfiguracaoLLM, modelo: str
) -> dict:
    url = montar_url_modelo(modelo)
    payload = montar_payload_gemini(
        prompt,
        temperatura=config.temperatura,
        max_tokens=config.max_tokens,
    )
    headers = {
        "x-goog-api-key": config.api_key,
        "Content-Type": "application/json",
    }

    inicio = time.perf_counter()
    with httpx.Client(timeout=config.timeout_segundos) as client:
        resposta = client.post(url, json=payload, headers=headers)
        resposta.raise_for_status()
        dados = resposta.json()

    duracao_ms = int((time.perf_counter() - inicio) * 1000)
    logger.info("chamada_llm status=%s duracao_ms=%d", resposta.status_code, duracao_ms)
    return dados


def chamar_llm_com_contingencia(prompt: str, config: ConfiguracaoLLM) -> dict:
    modelos = [config.modelo_principal, *config.modelos_fallback]
    ultimo_erro: httpx.HTTPStatusError | None = None

    for indice, modelo in enumerate(modelos):
        try:
            return enviar_requisicao_modelo(prompt, config, modelo)
        except httpx.HTTPStatusError as exc:
            ultimo_erro = exc
            status = exc.response.status_code
            logger.warning("falha_http status=%s tentativa=%d", status, indice + 1)
            tem_proximo = indice < len(modelos) - 1
            if status in (404, 503) and tem_proximo:
                if status == 503:
                    time.sleep(1.5)
                continue
            raise

    assert ultimo_erro is not None
    raise ultimo_erro
