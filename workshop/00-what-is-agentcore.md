# Amazon Bedrock AgentCore — co to jest i po co

## Problem

Zbudowanie agenta AI w POC to kilka godzin. Przeniesienie go do produkcji to miesiące:
- Session management
- Identity i auth
- Memory (pamięć między sesjami)
- Observability (co agent robi pod maską)
- Skalowanie
- Bezpieczeństwo

## Rozwiązanie

**Amazon Bedrock AgentCore** — zestaw managed services do deploymentu i operowania agentami AI w produkcji. Działa z dowolnym frameworkiem (Strands, LangGraph, CrewAI) i dowolnym modelem.

---

## Usługi AgentCore

### AgentCore Runtime
Serverless runtime do deployowania agentów. Obsługuje dowolny framework, auto-skaluje, izoluje sesje, szybki cold start. Deploy = `agentcore deploy` i działa.

**W warsztacie**: Lab 4 — deployujesz agenta do produkcji.

### AgentCore Memory
Managed pamięć dla agentów. Short-term memory (kontekst rozmowy) i long-term memory (preferencje usera, fakty z przeszłych sesji). Agenty pamiętają klientów między sesjami.

**W warsztacie**: Lab 2 — agent pamięta preferencje klienta.

### AgentCore Gateway
Centralny hub do narzędzi agentów. Zamienia Lambda, API, serwisy na MCP-kompatybilne toole. Semantic search po toolach, JWT auth, jeden endpoint dla wielu agentów.

**W warsztacie**: Lab 3 — Lambda z warranty check i web search jako MCP tools.

### AgentCore Identity
Zarządzanie tożsamością agentów. Integracja z Cognito/istniejącymi identity providers. Token vault dla bezpiecznego dostępu do narzędzi bez consent fatigue.

**W warsztacie**: Lab 3 — Cognito JWT authorizer na Gateway.

### AgentCore Observability
Traces, logi, dashboardy. Widać każdy krok agenta: reasoning LLM, tool calls, timings, token usage. Bazuje na OpenTelemetry.

**W warsztacie**: Lab 4 — CloudWatch GenAI Observability z pełnym drzewem wywołań.

### AgentCore Evaluations
Automatyczna ocena jakości agenta. Built-in evaluators: GoalSuccessRate, Correctness, ToolSelectionAccuracy. Online evaluation = ciągły monitoring produkcyjnego agenta.

**W warsztacie**: Lab 5 — konfiguracja online eval, 5 test scenarios, wyniki w CloudWatch.

### AgentCore Policy
Kontrola dostępu do narzędzi przez polityki Cedar. Agent może używać tylko tych toolów, na które pozwala policy. Enforcement poza kodem agenta.

**W warsztacie**: Lab 3 (opcjonalnie) — Cedar policy na Gateway.

### AgentCore Harness
Agent w jednym API call. Bez frameworka, bez Dockera, bez deployu. Podajesz model + prompt + tools, AWS uruchamia agenta w izolowanym Firecracker microVM.

**W warsztacie**: Lab 7 — `create_harness()` → `invoke_harness()` → agent działa.

### AgentCore Code Interpreter
Bezpieczne wykonywanie kodu w sandboxie. Agent może pisać i uruchamiać Python/JS w izolowanym środowisku.

**W warsztacie**: nie używamy.

### AgentCore Browser
Cloud-based przeglądarka dla agentów. Agent może nawigować strony, klikać, wypełniać formularze — skalowalne i bezpieczne.

**W warsztacie**: nie używamy.

### AgentCore Payments
Mikrotransakcje dla agentów. Agent płaci za płatne API, MCP toole, paywall content. Stablecoin (USDC), protokół x402, budżety per sesja.

**W warsztacie**: Lab 8 (overview/opowiadanie).

---

## Jak to łączymy w warsztacie

```
Lab 1: Agent Prototype
  └── Strands Agent + Nova Lite + 4 toole (local)

Lab 2: + Memory
  └── AgentCore Memory (STM + LTM, preferencje klienta)

Lab 3: + Gateway + Identity
  └── AgentCore Gateway (MCP tools via Lambda)
  └── Cognito JWT auth

Lab 4: + Runtime + Observability
  └── AgentCore Runtime (deploy do produkcji)
  └── CloudWatch traces

Lab 5: + Evaluations
  └── Online eval (GoalSuccessRate, Correctness, ToolSelection)

Lab 6: + Frontend
  └── Streamlit chat UI + Cognito login

Lab 7: Harness (standalone)
  └── Agent w jednym API call, Firecracker microVM

Lab 8: Payments (overview)
  └── Mikrotransakcje, x402, Coinbase/Stripe
```

## Linki

- [AgentCore Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AgentCore Starter Toolkit](https://github.com/awslabs/amazon-bedrock-agentcore-starter-toolkit)
- [AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
- [Launch blog post](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore/)
