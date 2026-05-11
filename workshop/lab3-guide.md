# Lab 3: Scale with Gateway and Identity

**Czas**: ~15-20 minut  
**Koszt**: ~$0.20 (Gateway + model invocations)  
**Co tworzymy**: AgentCore Gateway z Lambda targetem, Cognito auth, MCP client w agencie

## Co się dzieje w tym labie

1. Cognito setup — helper tworzy nowy User Pool + user `testuser` + bearer token
2. Tworzymy AgentCore Gateway (MCP protocol) z JWT authorizer
3. Dodajemy Lambda target — warranty check + web search jako MCP tools
4. Łączymy agenta z Gateway przez `MCPClient` — agent ma teraz 5 tools (3 lokalne + 2 MCP)
5. [Opcjonalnie] Cedar Policy Engine dla fine-grained access control

## Uruchomienie

```bash
cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1

python /path/to/workshop/lab3.py

# Z opcjonalnym Policy Engine:
ENABLE_POLICY_ENGINE=true python /path/to/workshop/lab3.py
```

## Architektura Lab 3

```
[User Query]
    ↓
[Strands Agent + Nova 2 Lite + Memory]
    ↓ (wybiera tool)
    ├── get_product_info()       → local mock
    ├── get_return_policy()      → local mock
    ├── get_technical_support()  → Bedrock KB (local tool)
    │
    └── [MCPClient → AgentCore Gateway (HTTPS + JWT)]
            ├── check_warranty_status → Lambda → DynamoDB
            └── web_search           → Lambda → DuckDuckGo
```

## Typowe błędy

| Błąd | Przyczyna | Rozwiązanie |
|------|-----------|-------------|
| `ResourceExistsException` na create_gateway | Gateway już istnieje | Skrypt jest idempotentny — użyje istniejącego |
| `ConflictException` na create_gateway_target | Target już istnieje | Normalne przy ponownym uruchomieniu |
| Bearer token expired | Token ważny ~1h | Uruchom ponownie — `get_or_create_cognito_pool(refresh_token=True)` |
| `AccessDenied` na MCP call | Zły token lub Gateway nie gotowy | Sprawdź `cognito_config['bearer_token']` |

## Zasoby stworzone w AWS

- **AgentCore Gateway**: `customersupport-gw` (ID w SSM)
- **Gateway Target**: `LambdaUsingSDK` (2 MCP tools)
- **Cognito User Pool**: `MCPServerPool` (dodatkowy, nie z CloudFormation)
- **Secrets Manager**: `customer_support_agent` (Cognito config)
- [Opcjonalnie] **Policy Engine** + 2 Cedar policies

## Następny krok

→ [Lab 4: Deploy to Production](lab4-guide.md)
