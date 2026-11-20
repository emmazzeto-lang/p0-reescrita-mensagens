def construir_prompt_reescrita(rascunho: str) -> str:
    texto_limpo = rascunho.strip()
    return (
        "Reescreva a mensagem ou o e-mail a seguir em um tom claro, direto e objetivo, "
        "mantendo o sentido original e sem inventar informacoes ou fatos novos.\n"
        "Retorne apenas o texto reescrito.\n\n"
        f"Rascunho:\n{texto_limpo}"
    )


def montar_payload_gemini(prompt: str) -> dict:
    return {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
