import httpx
from src.config import carregar_configuracao
from src.llm_client import chamar_llm_com_contingencia
from src.logger import configurar_logger
from src.presenter import exibir_mensagem_erro, exibir_resultado, formatar_erro_http
from src.prompt_builder import construir_prompt_reescrita
from src.response_handler import extrair_texto_resposta

logger = configurar_logger()


def capturar_entrada_usuario() -> str:
    print("Digite ou cole o rascunho da mensagem/e-mail e pressione Enter:")
    return input("> ").strip()


def executar_fluxo(rascunho: str) -> str | None:
    if not rascunho or not rascunho.strip():
        logger.info("fluxo_encerrado motivo=entrada_vazia")
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
        logger.warning("fluxo_interrompido motivo=configuracao_ou_resposta")
        exibir_mensagem_erro(str(exc))
        return None
    except httpx.TimeoutException:
        logger.warning("fluxo_interrompido motivo=timeout")
        exibir_mensagem_erro(
            "A requisicao excedeu o tempo limite de espera. Tente novamente."
        )
        return None
    except httpx.HTTPStatusError as exc:
        logger.warning("fluxo_interrompido motivo=http_%s", exc.response.status_code)
        exibir_mensagem_erro(formatar_erro_http(exc))
        return None
    except httpx.RequestError:
        logger.warning("fluxo_interrompido motivo=falha_rede")
        exibir_mensagem_erro(
            "Falha de comunicacao ao tentar acessar o servico do modelo. Verifique a conexao."
        )
        return None

    logger.info("fluxo_concluido status=sucesso")
    exibir_resultado(texto_final)
    return texto_final


def main() -> None:
    rascunho = capturar_entrada_usuario()
    executar_fluxo(rascunho)


if __name__ == "__main__":
    main()
