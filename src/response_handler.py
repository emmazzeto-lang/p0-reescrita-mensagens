def extrair_texto_resposta(dados: object) -> str:
    if not isinstance(dados, dict):
        raise ValueError("A resposta do modelo veio em formato inesperado.")

    candidatos = dados.get("candidates")
    if not isinstance(candidatos, list) or not candidatos:
        raise ValueError("O modelo nao retornou nenhuma resposta.")

    primeiro = candidatos[0]
    if not isinstance(primeiro, dict):
        raise ValueError("A resposta do modelo veio em formato inesperado.")

    conteudo = primeiro.get("content")
    if not isinstance(conteudo, dict):
        raise ValueError("A resposta do modelo veio em formato inesperado.")

    partes = conteudo.get("parts")
    if not isinstance(partes, list) or not partes:
        raise ValueError("A resposta do modelo veio sem conteudo textual.")

    texto = "".join(
        parte.get("text", "")
        for parte in partes
        if isinstance(parte, dict) and isinstance(parte.get("text"), str)
    ).strip()

    if not texto:
        raise ValueError("A resposta do modelo veio vazia.")

    return texto
