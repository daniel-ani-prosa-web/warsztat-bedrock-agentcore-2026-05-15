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

python /path/to/workshop/lab5.py
```

## Wyniki

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
