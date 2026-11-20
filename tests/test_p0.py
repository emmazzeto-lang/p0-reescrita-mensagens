import httpx
import pytest
from src import config as cfg_module
from src import llm_client, main as app_main, response_handler


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            req = httpx.Request("POST", "https://exemplo.local/v1beta/models/teste:generateContent")
            resp = httpx.Response(self.status_code, request=req)
            raise httpx.HTTPStatusError(f"HTTP {self.status_code}", request=req, response=resp)

    def json(self) -> dict:
        return self._payload


class _FakeClient:
    def __init__(self, response: _FakeResponse, timeout: float = 30.0):
        self._response = response
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url: str, json: dict, headers: dict):
        return self._response


def test_entrada_vazia_retorna_none(monkeypatch, capsys):
    monkeypatch.setattr(cfg_module, "carregar_configuracao", lambda: (_ for _ in ()).throw(AssertionError("Nao deve chamar config")))
    resultado = app_main.executar_fluxo("   ")
    saida = capsys.readouterr().out
    assert resultado is None
    assert "Entrada vazia" in saida


def test_credencial_ausente_gera_erro_claro(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    with pytest.raises(ValueError, match="Credencial ausente"):
        cfg_module.carregar_configuracao()


def test_configuracao_parametros_personalizados(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-teste")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.1")
    monkeypatch.setenv("LLM_MAX_TOKENS", "256")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "15")

    cfg = cfg_module.carregar_configuracao()
    assert cfg.temperatura == 0.1
    assert cfg.max_tokens == 256
    assert cfg.timeout_segundos == 15.0


def test_fluxo_completo_com_resposta_simulada(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-teste")
    monkeypatch.setenv("GEMINI_FALLBACK_MODELS", "")

    fake_resp = _FakeResponse(
        200,
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Ola, Fulano. Podemos adiar a entrega para sexta de manha?"}
                        ]
                    }
                }
            ]
        },
    )
    monkeypatch.setattr(httpx, "Client", lambda timeout=30.0: _FakeClient(fake_resp, timeout))

    texto = app_main.executar_fluxo("oi fulano da pra adiar pra sexta de manha?")
    assert texto == "Ola, Fulano. Podemos adiar a entrega para sexta de manha?"


def test_erro_simulado_credencial_invalida_403(monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "chave-invalida-simulada")
    monkeypatch.setenv("GEMINI_FALLBACK_MODELS", "")

    fake_resp = _FakeResponse(403, {"error": {"message": "API key not valid."}})
    monkeypatch.setattr(httpx, "Client", lambda timeout=30.0: _FakeClient(fake_resp, timeout))

    resultado = app_main.executar_fluxo("rascunho de teste")
    saida = capsys.readouterr().out
    assert resultado is None
    assert "403" in saida


def test_resposta_vazia_detectada():
    with pytest.raises(ValueError, match="vazia"):
        response_handler.extrair_texto_resposta(
            {"candidates": [{"content": {"parts": [{"text": "   "}]}}]}
        )
