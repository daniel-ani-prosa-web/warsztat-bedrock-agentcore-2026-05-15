# Lab 4: Deploy to Production with AgentCore Runtime

**Czas**: ~20-30 minut (w tym ~10 min na Docker build + deploy)  
**Koszt**: ~$1-5 (Runtime billed per-second while active!)  
**Co tworzymy**: Containerized agent deployed to AgentCore Runtime z full observability  
**Wymaga**: Docker Desktop running

## Co się dzieje w tym labie

1. Weryfikujemy Memory + Cognito token
2. Tworzymy IAM execution role dla Runtime
3. Starter toolkit generuje `Dockerfile` + `.bedrock_agentcore.yaml`
4. Docker build → ECR push → AgentCore Runtime deploy
5. Testujemy agent endpoint z session continuity
6. Obserwujemy traces w CloudWatch GenAI Observability

## Uruchomienie

```bash
# WAŻNE: Docker musi być uruchomiony!
docker info  # sprawdź czy działa

cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1

python ../../workshop/lab4.py
```

## Co trwa najdłużej

| Krok | Czas |
|------|------|
| IAM role creation | ~5 sekund |
| Runtime configure (Dockerfile gen) | ~5 sekund |
| Docker build + ECR push | ~3-5 minut |
| Runtime deploy (CREATING → READY) | ~3-5 minut |
| Test invocations | ~30 sekund |

## Typowe błędy

| Błąd | Przyczyna | Rozwiązanie |
|------|-----------|-------------|
| `Platform Mismatch WARNING` | Apple Silicon ARM vs x86 | Ignoruj — workshop mówi że OK |
| `Cannot connect to Docker daemon` | Docker nie uruchomiony | Uruchom Docker Desktop |
| `READY` nie przychodzi >10 min | Deploy problem | Sprawdź CloudWatch logs |
| `ConflictException` na launch | Agent o tej nazwie istnieje | Użyj `launch(auto_update_on_conflict=True)` |
| Bearer token expired | Token ważny ~1h | Uruchom ponownie — auto-refresh |

## Zasoby stworzone w AWS

- **IAM Role**: `CustomerSupportAssistantBedrockAgentCoreRole-{region}`
- **IAM Policy**: `CustomerSupportAssistantBedrockAgentCorePolicy-{region}`
- **ECR Repository**: `bedrock-agentcore-customer_support_agent-*`
- **AgentCore Runtime**: agent deployment (ARN w SSM)
- **CloudWatch Log Group**: Runtime logs

## UWAGA: Runtime kosztuje dopóki działa!

Runtime jest billed per-second. Po zakończeniu testów przejdź od razu do cleanup albo ręcznie usuń:

```bash
aws bedrock-agentcore-control delete-agent-runtime --agent-runtime-id RUNTIME_ID --region us-east-1
```

## Observability — eksploracja w CloudWatch (5 min)

Po testowych invocations poświęćcie chwilę na obejrzenie traces w konsoli AWS. To najlepsza wizualizacja tego co agent robi "pod maską".

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

### Wymagane

Jeśli traces się nie pojawiają — włącz **CloudWatch Transaction Search**:
CloudWatch → Settings → Transaction Search → Enable

[Dokumentacja](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Enable-TransactionSearch.html)

## Następny krok

→ [Lab 5: Evaluations](lab5-guide.md)
