# Lab 5: Evaluate Agent Performance

**Czas**: ~10-15 minut  
**Koszt**: ~$0.50 (5 invocations + evaluation processing)  
**Wymaga**: Runtime z Lab 4 aktywny!

## Co sie dzieje w tym labie

1. Pobieramy agent ARN z SSM (z Lab 4)
2. Tworzymy online evaluation config z 3 built-in evaluators
3. Odpalamy 5 test scenarios ktore generuja traces
4. Wyniki widoczne w CloudWatch GenAI Observability dashboard

## Evaluators

| Evaluator | Co mierzy |
|-----------|-----------|
| `Builtin.GoalSuccessRate` | Czy agent osiagnal cel klienta |
| `Builtin.Correctness` | Czy odpowiedz jest faktycznie poprawna |
| `Builtin.ToolSelectionAccuracy` | Czy agent wybral wlasciwe narzedzie |

## Uruchomienie

```bash
cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1

python ../../workshop/lab5.py
```

## Co zobaczysz po uruchomieniu

```
Region: us-east-1

--- Step 1: Retrieving agent info from Lab 4 ---
Agent ID: ag-XXXXXXXXXX
Agent ARN: arn:aws:bedrock-agentcore:us-east-1:123456789012:...

--- Step 2: Creating online evaluation configuration ---
Evaluators: GoalSuccessRate, Correctness, ToolSelectionAccuracy
Sampling rate: 100%
Configuration ID: eval-XXXXXXXXXX

--- Step 3: Verifying configuration ---
{ "onlineEvaluationConfigId": "eval-XXXXXXXXXX", ... }

--- Step 4: Generating test interactions for evaluation ---
  [Product info]: I need information about the Gaming Console Pro...
  Response: "The Gaming Console Pro features a 4K display..."

  [Tech support]: My laptop won't start up...
  Response: "I'd be happy to help troubleshoot..."

  [Return policy]: I bought a smartphone last week...
  Response: "Our return policy allows returns within 30 days..."

  [Multi-tool]: Check warranty for serial MNO33333333...
  Response: "I checked the warranty and it shows..."

  [Capabilities]: What kind of support can you provide?...
  Response: "I can help with product information..."

--- Lab 5 Complete ---
Evaluation config ID: eval-XXXXXXXXXX
View results in CloudWatch: https://console.aws.amazon.com/cloudwatch/...
```

5 test queries generuje traces. Evaluators automatycznie oceniaja kazdy trace.

## Wyniki w CloudWatch

Po zakonczeniu, sprawdz dashboard:
CloudWatch → GenAI Observability → Bedrock AgentCore → agent → DEFAULT endpoint

Wyniki moga pojawic sie z opoznieniem 2-5 minut.

## Typowe bledy

| Blad | Przyczyna | Rozwiazanie |
|------|-----------|-------------|
| `ParameterNotFound` runtime_arn | Lab 4 nie odpalony | Uruchom lab4.py najpierw |
| Runtime not READY | Runtime usuniety lub w trakcie | Uruchom lab4.py ponownie |
| Bearer token expired | Token wazny ~1h | Auto-refresh w skrypcie |

## Nastepny krok

→ [Lab 6: Frontend](lab6-guide.md)
