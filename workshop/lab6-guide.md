# Lab 6: Build a Customer-Facing Frontend

**Czas**: ~5-10 minut  
**Koszt**: $0 (frontend jest lokalny, Runtime z Lab 4 juz billed)  
**Wymaga**: Labs 1-4 wykonane, Runtime READY, NIE robic cleanup przed tym labem!

## Co sie dzieje w tym labie

Streamlit app ktore laczy sie z deployed Runtime endpoint z Lab 4:
- Cognito login w przegladarce
- Chat interface ze streaming responses
- Session management z persistent memory (Lab 2)
- Response timing per message

## Architektura

```
Przegladarka (localhost:8501)
    │
    ├── Cognito login (JWT token)
    │
    └── POST /runtimes/{arn}/invocations
         │  + Bearer token
         │  + Session ID
         │
         ▼
    AgentCore Runtime (Lab 4)
         │
         ├── Strands Agent + tools (Lab 1)
         ├── Memory (Lab 2)
         └── Gateway tools (Lab 3)
```

## Krok 1: Sprawdz czy Runtime dziala

```bash
cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1

# Sprawdz status Runtime
python - <<'PY'
import boto3

client = boto3.client("bedrock-agentcore-control")
for runtime in client.list_agent_runtimes().get("agentRuntimes", []):
    print(runtime["agentRuntimeId"], runtime["status"])
PY
```

Status runtime z Lab 4 musi byc `READY`. Jesli nie ma nic — wrocz do Lab 4.

## Krok 2: Doinstaluj frontend dependencies

```bash
uv pip install -r lab_helpers/lab5_frontend/requirements.txt
```

Instaluje: `streamlit`, `requests`, `boto3`, `streamlit-cognito-auth`

Uzywaj `uv pip` po aktywacji `.venv`. Na macOS zwykle `pip install ...` bezposrednio po `source .venv/bin/activate` potrafi trafic w systemowego Pythona 3.9/user site, a wtedy `streamlit` nie bedzie widoczny w srodowisku warsztatu.

## Krok 3: Odpal Streamlit

```bash
cd lab_helpers/lab5_frontend/
python -m streamlit run main.py
```

Output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Otworz `http://localhost:8501` w przegladarce.

## Krok 4: Zaloguj sie

Zobaczysz formularz logowania Cognito.

- **Username**: `testuser`
- **Password**: `MyPassword123!`

Te credentials stworzyl Lab 3 (`get_or_create_cognito_pool`). Po zalogowaniu zobaczysz sidebar z "Welcome, testuser" i pole czatu.

## Krok 5: Testuj agenta

Wpisz pytania w pole czatu i obserwuj:

| Scenariusz | Przykladowy prompt |
|------------|-------------------|
| Product info | "What are the specifications for your laptops?" |
| Return policy | "What's the return policy for electronics?" |
| Troubleshooting | "My iPhone is overheating, what should I do?" |
| Warranty check | "Check warranty for serial ABC12345678" |

### Co obserwowac

- **Streaming** — odpowiedz pojawia sie stopniowo, nie cala na raz
- **Response time** — pod kazda odpowiedzia jest czas w sekundach
- **Memory** — porozmawiaj, odswierz strone (F5), zapytaj o cos co juz mowiles — agent pamięta
- **Tool usage** — agent uzywa roznych narzedzi w zaleznosci od pytania

## Krok 6: Zatrzymaj Streamlit

`Ctrl+C` w terminalu.

## Jak to dziala pod maską

1. `main.py` — Streamlit UI, Cognito auth via `streamlit-cognito-auth`, obsluga czatu
2. `chat.py` — `invoke_endpoint_streaming()` robi POST do `https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{arn}/invocations` z Bearer tokenem
3. `chat_utils.py` — formatowanie, SSM helper, URL rendering
4. `sagemaker_helper.py` — generuje URL (localhost poza SageMaker)

Agent ARN jest pobierany z SSM: `/app/customersupport/agentcore/runtime_arn` (zapisany w Lab 4).
Bearer token pochodzi z logowania Cognito w przegladarce.
Session ID jest generowany per sesje Streamlit — mapuje sie na AgentCore Memory sessions.

## Typowe bledy

| Blad | Przyczyna | Rozwiazanie |
|------|-----------|-------------|
| `ResourceNotFoundException` on secret | Lab 3 nie odpalony lub cleanup wykonany | Uruchom lab3.py od nowa |
| `ParameterNotFound` runtime_arn | Lab 4 nie odpalony | Uruchom lab4.py |
| 403 / Connection refused | Runtime nie READY lub usuniety | Sprawdz `list-agent-runtimes` |
| Login fails | Zle credentials lub pool usuniety | `testuser` / `MyPassword123!`, sprawdz Cognito w konsoli |
| `ModuleNotFoundError: streamlit` | Deps nie sa w `.venv` | Wroc do `09-AgentCore-E2E/strands-agents`, aktywuj `.venv`, odpal `uv pip install -r lab_helpers/lab5_frontend/requirements.txt`, potem `python -m streamlit run main.py` |
| Timeout / brak odpowiedzi | Runtime cold start | Poczekaj 10-15s, sprobuj ponownie |

## Eksploracja w konsoli AWS

Po przetestowaniu frontendu, wrocz do CloudWatch:
**CloudWatch → GenAI Observability → Bedrock AgentCore → agent → DEFAULT**

Zobaczysz nowe traces — tym razem z frontendu. Porownaj z traces z Lab 4/5 (CLI).
Roznica: session ID z frontendu jest inny, wiec agent tworzy nowa sesje memory.

## Nastepny krok

→ [Cleanup](cleanup-guide.md) (OBOWIAZKOWE — Runtime kosztuje dopoki dziala!)
