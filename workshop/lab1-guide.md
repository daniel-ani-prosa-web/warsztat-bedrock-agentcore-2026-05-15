# Lab 1: Customer Support Agent Prototype

**Czas**: ~10-15 minut  
**Koszt**: ~$0.10 (model invocations only)  
**Co tworzymy**: Agent z 4 narzędziami (return policy, product info, web search, knowledge base) używający Strands Agents + Amazon Nova 2 Lite

## Co się dzieje w tym labie

1. Synchronizujemy Bedrock Knowledge Base (6 dokumentów technicznych uploadowanych przez CloudFormation)
2. Definiujemy 4 toole jako Python functions z dekoratorem `@tool`
3. Tworzymy agenta Strands z modelem Nova 2 Lite
4. Testujemy 3 pytania klienta — agent automatycznie wybiera odpowiednie toole

## Uruchomienie

```bash
# Upewnij się że jesteś w katalogu strands-agents z aktywnym venv
cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate

# Ustaw credentials
export AWS_PROFILE=personal  # <- zmień na swój profil
export AWS_REGION=us-east-1   # <- zmień na swój region

# Odpal lab
python ../../workshop/lab1.py
```

## Oczekiwany output

```
Account: XXXXXXXXXXXX  Region: us-east-1

--- Step 1: Syncing Bedrock Knowledge Base ---
Knowledge Base ID: XXXXXXXXXX
Data Source ID:    XXXXXXXXXX
Ingestion job started: XXXXXXXXXX
  Status: STARTING
  Status: IN_PROGRESS
  Status: COMPLETE
KB sync complete — 6 documents ingested

--- Step 2: Defining agent tools ---
All 4 tools ready: get_return_policy, get_product_info, web_search, get_technical_support

--- Step 3: Creating Customer Support Agent ---
Agent created successfully!

--- Step 4: Testing the agent ---
(... odpowiedzi agenta na 3 pytania testowe ...)

--- Lab 1 Complete ---
```

## Typowe błędy

| Błąd | Przyczyna | Rozwiązanie |
|------|-----------|-------------|
| `No matching distribution found for strands-agents` | Python 3.14+ | Użyj Python 3.13: `uv venv .venv --python 3.13` |
| `Unable to locate credentials` | Brak AWS credentials | `export AWS_PROFILE=xxx` lub `aws configure` |
| `AccessDeniedException` na `InvokeModel` | Nova 2 Lite nie włączona | Bedrock Console → Model Access → Enable `Amazon Nova 2 Lite` |
| `ParameterNotFound` na KB ID | `prereq.sh` nie uruchomiony | Wróć do Setup i uruchom `prereq.sh` |
| `RatelimitException` w web_search | DuckDuckGo rate limit | Poczekaj minutę i spróbuj ponownie — to nie wpływa na resztę |

## Co zostało stworzone

Żadne nowe zasoby AWS. Lab 1 tylko czyta z istniejących zasobów (KB, SSM, model).

## Architektura Lab 1

```
[User Query]
    ↓
[Strands Agent + Nova 2 Lite]
    ↓ (wybiera tool)
    ├── get_return_policy()    → mock data (local)
    ├── get_product_info()     → mock data (local)
    ├── web_search()           → DuckDuckGo API (internet)
    └── get_technical_support() → Bedrock Knowledge Base (AWS)
```

## Następny krok

→ [Lab 2: Enhance with Memory](lab2-guide.md)
