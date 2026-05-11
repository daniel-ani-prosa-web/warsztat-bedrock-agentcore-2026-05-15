# Lab 4: Deploy to Production with AgentCore Runtime

**Czas**: ~20-30 minut (w tym ~10 min na build + deploy server-side)  
**Koszt**: ~$1-5 (Runtime billed per-second while active!)  
**Co tworzymy**: Agent zdeployowany do AgentCore Runtime z observability

## Co się dzieje w tym labie

1. Weryfikujemy Memory + Cognito token (z Lab 2 i 3)
2. Tworzymy IAM execution role dla Runtime
3. Starter toolkit generuje `Dockerfile` + `.bedrock_agentcore.yaml` (lokalnie, jako config)
4. `runtime.launch()` wysyła kod do AWS → **CodeBuild** buduje Docker image → pushuje do ECR → deployuje Runtime
5. Czekamy na status `READY`
6. Testujemy agent endpoint z bearer tokenem i session ID

**Docker Desktop NIE jest wymagany.** Cały build odbywa się server-side w AWS CodeBuild.

## Uruchomienie

```bash
cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1

python ../../workshop/lab4.py
```

## Co zobaczysz po uruchomieniu

```
Region: us-east-1

--- Step 1: Ensuring Memory exists ---
Memory CustomerSupportMemory: mem-XXXXXXXXXX

--- Step 2: Creating IAM execution role ---
Role ARN: arn:aws:iam::123456789012:role/CustomerSupportAssistant...

--- Step 3: Getting Cognito token ---
Bearer token obtained.

--- Step 4: Configuring Runtime ---
Generated: Dockerfile, .bedrock_agentcore.yaml

--- Step 5: Launching to AgentCore Runtime ---
  Building... (CodeBuild, server-side)
  Status: CREATING
  Status: CREATING
  ...
  Status: READY
Agent deployed! ARN: arn:aws:bedrock-agentcore:us-east-1:...

--- Step 6: Testing deployed agent ---
Query: "What is the return policy for electronics?"
Response: "Our return policy for electronics allows returns
           within 30 days of purchase..."

Query: "Check warranty for serial ABC12345678"
Response: "I checked the warranty status for serial ABC12345678..."

--- Lab 4 Complete ---
```

Build trwa ~3-5 minut (CodeBuild). Deploy kolejne ~3-5 minut. Razem ~10 minut czekania.

## Co trwa najdłużej

| Krok | Czas |
|------|------|
| IAM role creation | ~5 sekund |
| Runtime configure (Dockerfile gen) | ~5 sekund |
| CodeBuild (server-side Docker build + ECR push) | ~3-5 minut |
| Runtime deploy (CREATING → READY) | ~3-5 minut |
| Test invocations | ~30 sekund |

## Typowe błędy

| Błąd | Przyczyna | Rozwiązanie |
|------|-----------|-------------|
| `Platform Mismatch WARNING` | Apple Silicon ARM vs x86 | Ignoruj — build jest server-side, nie lokalny |
| `READY` nie przychodzi >10 min | Deploy problem | Sprawdź CloudWatch logs |
| `ConflictException` na launch | Agent o tej nazwie istnieje | Skrypt używa `auto_update_on_conflict=True` |
| Bearer token expired | Token ważny ~1h | Uruchom ponownie — auto-refresh |

## Zasoby stworzone w AWS

- **IAM Role**: `CustomerSupportAssistantBedrockAgentCoreRole-{region}`
- **IAM Policy**: `CustomerSupportAssistantBedrockAgentCorePolicy-{region}`
- **ECR Repository**: `bedrock-agentcore-customer_support_agent-*`
- **AgentCore Runtime**: agent deployment (ARN w SSM)
- **CloudWatch Log Group**: Runtime logs

## UWAGA: Runtime kosztuje dopóki działa!

Runtime jest billed per-second. Po zakończeniu testów przejdź do Lab 5/6 albo od razu do cleanup.

Ręczne usunięcie:
```bash
aws bedrock-agentcore-control delete-agent-runtime --agent-runtime-id RUNTIME_ID --region us-east-1
```

## Observability — eksploracja w CloudWatch (5 min)

Po testowych invocations otwórzcie konsolę AWS i obejrzyjcie traces. To najlepsza wizualizacja tego co agent robi "pod maską".

### Jak otworzyć

1. AWS Console → **CloudWatch** → lewy panel → **GenAI Observability** → **Bedrock AgentCore**
2. Znajdź swojego agenta na liście → kliknij **DEFAULT** endpoint
3. Kliknij dowolny **trace** z listy

### Co zobaczycie

- **Pełne drzewo wywołań** — od promptu usera, przez reasoning LLM, po każdy tool call
- **Timings** — ile trwał każdy krok (LLM inference vs tool execution)
- **Tool calls** — jakie narzędzia agent wybrał, z jakimi parametrami, co zwróciły
- **Token usage** — ile tokenów zużyło każde wywołanie LLM
- **Errors** — jeśli coś poszło nie tak, tu będzie root cause

### Przykładowy trace flow

```
Agent Invocation (total: ~8s)
├── LLM Call #1 - reasoning (2.1s, 450 tokens)
│   └── Decision: use get_product_info tool
├── Tool: get_product_info (0.3s)
├── LLM Call #2 - reasoning (1.8s, 380 tokens)
│   └── Decision: use web_search tool
├── Tool: web_search (1.2s)
└── LLM Call #3 - final response (2.6s, 520 tokens)
```

### Jeśli traces się nie pojawiają

Włącz **CloudWatch Transaction Search**:
CloudWatch → Settings → Transaction Search → Enable

[Dokumentacja](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Enable-TransactionSearch.html)

## Następny krok

→ [Lab 5: Evaluations](lab5-guide.md)
