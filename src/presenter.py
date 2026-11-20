import httpx


def formatar_erro_http(exc: httpx.HTTPStatusError) -> str:
    status = exc.response.status_code
    detalhe = ""
    try:
        corpo = exc.response.json()
        if isinstance(corpo, dict):
            erro = corpo.get("error")
            if isinstance(erro, dict) and isinstance(erro.get("message"), str):
                detalhe = erro["message"].strip()
    except Exception:
        detalhe = ""

    extra = f" Detalhe: {detalhe}" if detalhe else ""

    if status in (401, 403):
        return (
            f"Credencial invalida ou sem permissao para acessar o modelo (HTTP {status}). "
            f"Verifique a chave configurada.{extra}"
        )
    if status == 400:
        return (
            "Requisicao invalida ou credencial/parametro rejeitado pelo servico (HTTP 400). "
            f"Verifique a configuracao do modelo e da chave.{extra}"
        )
    if status == 404:
        return (
            "Modelo ou endpoint nao encontrado (HTTP 404). "
            f"Verifique o identificador do modelo configurado.{extra}"
        )
    if status == 503:
        return (
            "O servico do modelo esta temporariamente indisponivel (HTTP 503). "
            f"Tente novamente em alguns instantes.{extra}"
        )
    if status >= 500:
        return (
            f"O servico do modelo apresentou indisponibilidade interna (HTTP {status}). "
            f"Tente novamente mais tarde.{extra}"
        )
    return f"Falha na chamada ao servico do modelo (HTTP {status}).{extra}"


def exibir_resultado(texto_reescrito: str) -> None:
    print("\n--- Versao clara e objetiva ---")
    print(texto_reescrito)


def exibir_mensagem_erro(mensagem: str) -> None:
    print(f"\nAviso: {mensagem}")
