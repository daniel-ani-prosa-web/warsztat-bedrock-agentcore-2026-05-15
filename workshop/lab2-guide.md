# Lab 2: Enhance Agent with Memory

**Czas**: ~15-20 minut (w tym 3 min na provisioning memory)  
**Koszt**: ~$0.20 (Memory provisioning + model invocations)  
**Co tworzymy**: AgentCore Memory z dwoma strategiami (preferences + semantic), integrujemy z agentem

## Co się dzieje w tym labie

1. Tworzymy AgentCore Memory resource (managed vector DB + processing pipelines)
2. Seedujemy 6 historycznych interakcji klienta
3. Czekamy na Long-Term Memory extraction (system automatycznie wyciąga preferencje + fakty)
4. Tworzymy agenta z `AgentCoreMemorySessionManager` — pamięta klienta między sesjami
5. Testujemy personalizowane odpowiedzi

## Uruchomienie

```bash
cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1

python ../../workshop/lab2.py
```

## Co zobaczysz po uruchomieniu

```
Region: us-east-1

--- Step 1: Creating AgentCore Memory ---
Memory CustomerSupportMemory already exists: mem-XXXXXXXXXX
  (lub: Creating memory... Status: CREATING... Status: ACTIVE)

--- Step 2: Seeding historical interactions ---
  Seeding interaction 1/6: laptop recommendation
  Seeding interaction 2/6: return policy question
  ...
  Seeding interaction 6/6: software update help
  All 6 interactions seeded.

--- Step 3: Waiting for LTM extraction ---
  Checking... 1/12 (processing takes ~60s)
  Checking... 5/12
  Found 3 extracted memories!
  Memory 1: USER_PREFERENCE — "Customer prefers eco-friendly products"
  Memory 2: SEMANTIC — "Customer had issues with laptop battery..."
  ...

--- Step 4: Creating memory-enhanced agent ---
Agent created with AgentCoreMemorySessionManager

--- Step 5: Testing personalized responses ---
Query: "Do you remember my preferences?"
Agent: "Based on our previous conversations, I can see you prefer
        eco-friendly products and have a laptop that..."

--- Lab 2 Complete ---
```

Agent odpowiada **spersonalizowanie** — zna historię klienta z seeded interactions.

## Co trwa najdłużej

| Krok | Czas |
|------|------|
| Memory provisioning (first run) | ~3 minuty |
| LTM extraction | ~60 sekund |
| Agent test queries | ~15 sekund |

## Typowe błędy

| Błąd | Przyczyna | Rozwiązanie |
|------|-----------|-------------|
| `ValidationException: X-Ray Delivery` | Brak CloudWatch Logs trace destination | Ignoruj — to warning, nie blokuje |
| Memory stays in CREATING >5 min | Rzadko — service delay | Odpal ponownie, `get_or_create_memory` jest idempotentny |
| `Still processing...` 12/12 z pustymi memories | LTM overloaded | Czekaj dłużej lub uruchom ponownie — processing jest async |

## Zasoby stworzone w AWS

- **AgentCore Memory**: `CustomerSupportMemory` (ID w SSM `/app/customersupport/agentcore/memory_id`)
- **CloudWatch Log Group**: `/aws/vendedlogs/bedrock-agentcore/memory/APPLICATION_LOGS/...`

## Kluczowe koncepty

```
[create_event()]  →  Short-Term Memory (natychmiast)
                          ↓ (async, ~30-60s)
                     Long-Term Memory
                          ├── USER_PREFERENCE: preferencje klienta
                          └── SEMANTIC: fakty z rozmów (vector embeddings)

[retrieve_memories()]  ←  query po namespace + similarity search
```

## Następny krok

→ [Lab 3: Scale with Gateway and Identity](lab3-guide.md)
