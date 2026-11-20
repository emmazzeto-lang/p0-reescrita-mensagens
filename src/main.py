import httpx
from src.config import carregar_configuracao
from src.llm_client import chamar_llm_com_contingencia
from src.presenter import exibir_mensagem_erro, exibir_resultado, formatar_erro_http
from src.prompt_builder import construir_prompt_reescrita
from src.response_handler import extrair_texto_resposta


def capturar_entrada_usuario() -> str:
    print("Digite ou cole o rascunho da mensagem/e-mail e pressione Enter:")
    return input("> ").strip()


def executar_fluxo(rascunho: str) -> str | None:
    if not rascunho or not rascunho.strip():
        exibir_mensagem_erro(
            "Entrada vazia. Digite ou cole um rascunho de mensagem ou e-mail antes de enviar."
        )
        return None

    try:
        config = carregar_configuracao()
        prompt = construir_prompt_reescrita(rascunho)
        dados_resposta = chamar_llm_com_contingencia(prompt, config)
        texto_final = extrair_texto_resposta(dados_resposta)
    except ValueError as exc:
        exibir_mensagem_erro(str(exc))
        return None
    except httpx.TimeoutException:
        exibir_mensagem_erro(
            "A requisicao excedeu o tempo limite de espera. Tente novamente."
        )
        return None
    except httpx.HTTPStatusError as exc:
        exibir_mensagem_erro(formatar_erro_http(exc))
        return None
    except httpx.RequestError:
        exibir_mensagem_erro(
            "Falha de comunicacao ao tentar acessar o servico do modelo. Verifique a conexao."
        )
        return None

    exibir_resultado(texto_final)
    return texto_final


def main() -> None:
    rascunho = capturar_entrada_usuario()
    executar_fluxo(rascunho)


if __name__ == "__main__":
    main()
