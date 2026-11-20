Markdown
# P0 — Reescrita Clara e Objetiva de Mensagens e E-mails

Aplicação em Python executada localmente via terminal para reescrever rascunhos de mensagens ou e-mails em um tom claro, direto e objetivo, preservando o sentido original sem adicionar fatos novos.

## Problema e Público
- **Problema:** Reescrever um rascunho de mensagem ou e-mail em um tom mais claro e objetivo.
- **Público:** Pessoas (estudantes, profissionais ou equipes) que redigem mensagens ou e-mails no dia a dia e desejam tornar rascunhos prolixos ou informais mais diretos e claros.
- **Por que usar um LLM:** Reescrever mantendo o sentido original e ajustando clareza e objetividade em linguagem natural exige interpretação de intenção e geração textual, não resolvida adequadamente por regras fixas.

## Funcionamento e Limites do Projeto
- **Funcionamento:** Recebe o rascunho via terminal, valida a entrada, carrega as configurações do ambiente, monta a instrução de reescrita, consulta a API REST do modelo configurado (com contingência configurável e tratamento de erros) e exibe o texto reescrito.
- **Limites do escopo (P0):** Aplicação Python local via terminal, chamada a um único provedor/modelo por execução (sem *tool calling* nativo), sem interface web, banco de dados, autenticação de usuários, RAG, agentes ou deploy em nuvem.

## Requisitos e Instalação
- **Python:** 3.11 ou superior.
- **Dependências:** listadas em `requirements.txt` (`httpx`, `python-dotenv`, `pytest`).

Passo a passo:

git clone [https://github.com/emmazzeto-lang/p0-reescrita-mensagens.git](https://github.com/emmazzeto-lang/p0-reescrita-mensagens.git)
cd p0-reescrita-mensagens
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copie .env.example para .env (o .env está ignorado no .gitignore e nunca deve conter chaves reais no repositório)
Variáveis suportadas (veja `.env.example`):
- `GEMINI_API_KEY` (ou `LLM_API_KEY`): chave de acesso ao provedor externo (opcionalmente substituível por configuração compatível com o endpoint institucional quando utilizado; o uso de provedor externo é facultativo, sob responsabilidade do estudante e sem suporte institucional).
- `GEMINI_MODEL` (ou `LLM_MODEL`): modelo principal (ex.: `gemini-3.5-flash-lite`).
- `GEMINI_FALLBACK_MODELS`: modelos alternativos separados por vírgula em caso de `404` ou `503`.
- `LLM_TIMEOUT_SECONDS`: tempo limite da requisição em segundos (padrão `30`).
- `LLM_TEMPERATURE`: temperatura de geração (padrão `0.2`).
- `LLM_MAX_TOKENS`: limite máximo de tokens de saída (padrão `512`).
- `LOG_LEVEL`: nível de registro simples sem dados sensíveis (padrão `INFO`).

**Distinção entre testes:**
- **Testes simulados (`pytest`):** executam localmente com respostas e erros simulados, **sem** fazer chamada real à API externa e sem exigir chave real.
- **Teste real (`python -m src.main`):** realiza chamada real pela rede ao endpoint configurado no `.env` e exige chave válida e conectividade.

## Execução
Com o ambiente virtual ativo e o `.env` configurado:

python -m src.main