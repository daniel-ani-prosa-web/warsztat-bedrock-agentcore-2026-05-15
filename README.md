# Amazon Bedrock AgentCore — Warsztat

**AWS User Group Wrocław, 15 maja 2026**

Hands-on workshop: budujemy Customer Support Agenta od prototypu do produkcji z Amazon Bedrock AgentCore.

## Start tutaj

Główny przewodnik dla uczestników: [workshop/WORKSHOP.md](workshop/WORKSHOP.md)

Repo zawiera też upstreamowe sample AWS w katalogach `09-AgentCore-E2E/` i `11-AgentCore-harness/`. Nie zaczynaj od nich. Traktuj je jako katalogi robocze wskazywane przez guide.

## Zanim zaczniesz

1. Przeczytaj co budujemy: [workshop/00-what-is-agentcore.md](workshop/00-what-is-agentcore.md)
2. Przygotuj środowisko: [workshop/00-prerequisites.md](workshop/00-prerequisites.md)
3. Sprawdź gotowość: `bash check-ready.sh`

## Instrukcje

Pełna mapa repo i katalogów roboczych: [workshop/REPO-STRUCTURE.md](workshop/REPO-STRUCTURE.md)

## Struktura

```
workshop/                    ← instrukcje + skrypty do odpalenia
  00-prerequisites.md        ← setup przed warsztatem
  WORKSHOP.md                ← master guide
  REPO-STRUCTURE.md          ← gdzie pracujemy w każdym labie
  lab1-guide.md .. lab8-guide.md
  lab1.py .. lab7-harness.py
  cleanup.py, cleanup-guide.md

09-AgentCore-E2E/            ← katalog roboczy Labs 1-6
  strands-agents/            ← Labs 1-6: Customer Support Agent E2E

11-AgentCore-harness/        ← katalog roboczy Lab 7
  00-getting-started/        ← Lab 7: Harness
```

## Labs

| Lab | Temat | Czas |
|-----|-------|------|
| 1 | Agent Prototype (Strands + Nova Lite) | 10-15 min |
| 2 | AgentCore Memory (STM + LTM) | 15-20 min |
| 3 | AgentCore Gateway + Identity | 15-20 min |
| 4 | AgentCore Runtime + Observability | 20-30 min |
| 5 | Online Evaluations | 10-15 min |
| 6 | Streamlit Frontend | 5-10 min |
| 7 | AgentCore Harness (standalone) | 5-10 min |
| 8 | AgentCore Payments (overview) | 10 min |

## Koszt

~$3-10 za pełny run. **Cleanup obowiązkowy po warsztacie.**

## Źródło

Bazuje na: [awslabs/amazon-bedrock-agentcore-samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
