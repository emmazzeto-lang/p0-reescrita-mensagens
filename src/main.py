import os
import time
from dotenv import load_dotenv
import httpx

load_dotenv()


def chamar_gemini(prompt: str, api_key: str, modelo: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=30.0) as client:
        resposta = client.post(url, json=payload, headers=headers)
        resposta.raise_for_status()
        dados = resposta.json()

    candidatos = dados.get("candidates", [])
    if not isinstance(candidatos, list) or not candidatos:
        raise RuntimeError("O modelo nao retornou nenhuma resposta.")

    partes = candidatos[0].get("content", {}).get("parts", [])
    if not isinstance(partes, list):
        raise RuntimeError("A resposta do modelo veio em formato inesperado.")

    texto_resposta = "".join(
        parte.get("text", "") for parte in partes if isinstance(parte, dict)
    ).strip()

    if not texto_resposta:
        raise RuntimeError("A resposta do modelo veio vazia.")

    return texto_resposta


def reescrever_mensagem(rascunho: str) -> str:
    api_key = (
        os.getenv("GEMINI_API_KEY", "").strip()
        or os.getenv("LLM_API_KEY", "").strip()
    )
    modelo_principal = (
        os.getenv("GEMINI_MODEL", "").strip()
        or os.getenv("LLM_MODEL", "").strip()
        or "gemini-3.5-flash-lite"
    )
    fallbacks_env = os.getenv(
        "GEMINI_FALLBACK_MODELS", "gemini-3.5-flash,gemini-flash-latest"
    )

    if not api_key:
        raise RuntimeError(
            "Chave de API nao encontrada. Defina GEMINI_API_KEY no arquivo .env."
        )

    prompt = (
        "Reescreva a mensagem ou o e-mail a seguir em um tom claro, direto e objetivo, "
        "mantendo o sentido original e sem inventar informacoes ou fatos novos.\n"
        "Retorne apenas o texto reescrito.\n\n"
        f"Rascunho:\n{rascunho}"
    )

    modelos_para_tentar = [modelo_principal]
    for alt in fallbacks_env.split(","):
        nome = alt.strip()
        if nome and nome not in modelos_para_tentar:
            modelos_para_tentar.append(nome)

    ultimo_erro_http = None
    for indice, modelo in enumerate(modelos_para_tentar):
        try:
            return chamar_gemini(prompt, api_key, modelo)
        except httpx.HTTPStatusError as exc:
            ultimo_erro_http = exc
            if exc.response.status_code in (404, 503) and indice < len(modelos_para_tentar) - 1:
                if exc.response.status_code == 503:
                    time.sleep(1.5)
                continue
            raise

    raise ultimo_erro_http  # type: ignore[misc]


def formatar_erro_http(exc: httpx.HTTPStatusError) -> str:
    status_code = exc.response.status_code
    detalhe = ""
    try:
        detalhe = exc.response.json().get("error", {}).get("message", "")
    except Exception:
        detalhe = ""

    sufixo = f" Detalhe: {detalhe}" if detalhe else ""

    if status_code == 503:
        return (
            "O servico do modelo esta temporariamente sobrecarregado (HTTP 503). "
            f"Tente novamente em alguns instantes.{sufixo}"
        )
    if status_code in (401, 403):
        return (
            f"Falha de autenticacao ou permissao com a API (HTTP {status_code}). "
            f"Verifique se a chave de API configurada e valida.{sufixo}"
        )
    if status_code == 400:
        return (
            "Requisicao invalida enviada ao servico do modelo (HTTP 400). "
            f"Verifique o identificador do modelo configurado.{sufixo}"
        )
    return f"Erro ao consultar o servico do modelo (HTTP {status_code}).{sufixo}"


def main() -> None:
    print("Digite ou cole o rascunho da mensagem/e-mail e pressione Enter:")
    rascunho = input("> ").strip()

    if not rascunho:
        print("Entrada vazia. Informe um rascunho de mensagem ou e-mail.")
        return

    try:
        resultado = reescrever_mensagem(rascunho)
    except httpx.TimeoutException:
        print("A requisicao ao modelo excedeu o tempo limite. Tente novamente.")
        return
    except httpx.HTTPStatusError as exc:
        print(formatar_erro_http(exc))
        return
    except httpx.RequestError:
        print("Falha de comunicacao ao tentar acessar o servico do modelo.")
        return
    except RuntimeError as exc:
        print(f"Erro de configuracao ou resposta: {exc}")
        return

    print("\n--- Versao clara e objetiva ---")
    print(resultado)


if __name__ == "__main__":
    main()
