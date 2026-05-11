# Getting Started with Amazon Bedrock AgentCore

Workshop AWS UG Wroclaw — Self-paced guide

## Czego sie nauczysz

Budujesz Customer Support Agenta od prototypu do produkcji:
- **Lab 1**: Agent z 4 narzedzmi (Strands Agents + Nova 2 Lite)
- **Lab 2**: Persistent memory (AgentCore Memory — STM + LTM)
- **Lab 3**: Centralized tools (AgentCore Gateway + Cognito auth)
- **Lab 4**: Production deploy (AgentCore Runtime + Observability)
- **Lab 5**: Online evaluations (GoalSuccessRate, Correctness, ToolSelectionAccuracy)
- **Lab 6**: Streamlit frontend (Cognito login, streaming chat, session management)
- **Lab 7**: AgentCore Harness — agent w jednym API call, zero frameworkow (standalone)
- **Lab 8**: AgentCore Payments — agenty z portfelem (opcjonalny, standalone)

**Czas**: ~2.5-3h (Labs 1-7), Lab 8 opcjonalny (+30 min)  
**Koszt**: ~$3-10 (cleanup w ciagu 2h od Lab 4)

---

## Co to jest AgentCore?

Przeczytaj: [00-what-is-agentcore.md](00-what-is-agentcore.md) — opis każdej usługi i jak łączą się w warsztacie.

---

## Wymagania

**Przeczytaj i wykonaj PRZED warsztatem**: [00-prerequisites.md](00-prerequisites.md)

| Co | Minimum |
|----|---------|
| Konto AWS | Osobiste z admin access (lub bliskim) |
| AWS CLI | Skonfigurowane z credentials (`aws sts get-caller-identity` musi dzialac) |
| Python | 3.10-3.13 (**NIE** 3.14 — `strands-agents` nie ma buildu) |
| uv | Opcjonalne ale zalecane (`pip install uv`) |
| Docker | Zainstalowany (Lab 4) — ale CodeBuild robi build server-side, wiec nie jest krytyczny |
| Bedrock Model Access | Auto-enable przy pierwszym invoke. Nic nie trzeba robic. |
| Git | Do klonowania repo |

### Bez lokalnego CLI?

Uzyj **AWS CloudShell** w konsoli — ma git, zip, AWS CLI, Python. Wklej komendy jak ponizej.

---

## Setup (10-15 minut)

### 1. Klonowanie repo

```bash
git clone <URL_REPO_WARSZTATU>
cd warsztat-bedrock-agentcore-2026-05-15/09-AgentCore-E2E/strands-agents
```

> URL repo zostanie podany na warsztacie.

### 2. Credentials i region

```bash
export AWS_PROFILE=personal   # <- zmien na swoj profil
export AWS_REGION=us-east-1    # <- zmien na swoj region
aws sts get-caller-identity    # sprawdz czy dziala
```

### 3. Python venv

```bash
uv venv .venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

Lub bez uv:
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Bedrock Model Access

Nic nie trzeba robic — modele aktywuja sie automatycznie przy pierwszym invoke.

### 5. Deploy infrastruktury

```bash
bash scripts/prereq.sh
```

Trwa ~10 minut. Tworzy:
- S3 bucket z Lambda code
- CloudFormation stack `CustomerSupportStackInfra` (DynamoDB, Lambda, Bedrock KB, IAM roles)
- CloudFormation stack `CustomerSupportStackCognito` (Cognito User Pool)

Weryfikacja:
```bash
bash scripts/list_ssm_parameters.sh
```

Powinno pokazac 13 SSM parametrow pod `/app/customersupport/*`.

---

## Labs

| Lab | Guide | Skrypt | Czas | Koszt |
|-----|-------|--------|------|-------|
| 1 | [lab1-guide.md](lab1-guide.md) | [lab1.py](lab1.py) | 10-15 min | ~$0.10 |
| 2 | [lab2-guide.md](lab2-guide.md) | [lab2.py](lab2.py) | 15-20 min | ~$0.20 |
| 3 | [lab3-guide.md](lab3-guide.md) | [lab3.py](lab3.py) | 15-20 min | ~$0.20 |
| 4 | [lab4-guide.md](lab4-guide.md) | [lab4.py](lab4.py) | 20-30 min | ~$1-5 |
| 5 | [lab5-guide.md](lab5-guide.md) | [lab5.py](lab5.py) | 10-15 min | ~$0.50 |
| 6 | [lab6-guide.md](lab6-guide.md) | Streamlit w repo | 5-10 min | $0 |
| 7 | [lab7-guide.md](lab7-guide.md) | [lab7-harness.py](lab7-harness.py) | 5-10 min | ~$0.05 |
| 8 | [lab8-guide.md](lab8-guide.md) | Demo/take-home | ~10 min (pokaz) | $0 |

Labs 1-6 buduja na sobie — nie pomijaj. Lab 7 i 8 sa **standalone** (niezalezne od 1-6).

---

## Cleanup (OBOWIAZKOWE)

```bash
python ../../workshop/cleanup.py
bash scripts/cleanup.sh
```

Szczegoly: [cleanup-guide.md](cleanup-guide.md)

**Runtime kosztuje dopoki nie usuniesz.** Nie zostawiaj na noc.

---

## Eksploracja w konsoli AWS

Po kazdym labie uczestnicy moga otworzyc konsole i zobaczyc co sie stalo. Najciekawsze:

| Po labie | Gdzie w konsoli | Co zobaczyc |
|----------|----------------|-------------|
| Setup | CloudFormation → Stacks | 2 stacki, Resources tab — lista wszystkiego co stworzyl |
| Setup | DynamoDB → Tables | `customer-products`, `customer-warranties` — mock dane |
| Setup | Lambda → Functions | `CustomerSupportFunction` — kod, test invocation |
| Lab 1 | Bedrock → Knowledge Bases | `CustomerSupportKB` — sync status, test query |
| Lab 2 | Bedrock → AgentCore → Memory | `CustomerSupportMemory` — sessions, extracted memories |
| Lab 3 | Bedrock → AgentCore → Gateway | `customersupport-gw` — targets, API spec |
| Lab 3 | Cognito → User Pools | `MCPServerPool` — users, app clients |
| Lab 4 | Bedrock → AgentCore → Agent Runtimes | Status, **Test playground** — wpisz prompt! |
| Lab 4 | CloudWatch → GenAI Observability → AgentCore | **Traces** — pelny call tree, tool calls, timings |
| Lab 5 | CloudWatch → GenAI Observability → AgentCore | Evaluation scores (GoalSuccessRate, Correctness, ToolSelection) |
| Lab 5 | Bedrock → AgentCore → Evaluations | Online eval config, status |

**Tip**: Niech uczestnicy otwieraja console w osobnym tabie. Po kazdym labie 2-3 minuty na eksploracje — daje lepsze zrozumienie niz sam CLI.

---

## Znane problemy i gotchas

### Python
- Python 3.14 **nie dziala** z `strands-agents`. Uzyj 3.13 lub nizej.

### Model access
- Model ID: `global.amazon.nova-2-lite-v1:0` (cross-region inference profile). Auto-enable przy pierwszym invoke.

### prereq.sh
- Trwa ~10 min. NIE przerywaj. CloudFormation kontynuuje server-side, ale skrypt nie wie o tym.
- Idempotentny — mozna odpalic ponownie bezpiecznie.

### Lab 2 (Memory)
- Memory provisioning: ~3 minuty na pierwsze tworzenie. Cierpliwie czekaj.
- LTM extraction: ~60 sekund async. Moze byc dluzej przy obciazeniu.
- X-Ray warning (`ValidationException`) — ignoruj, nie blokuje.

### Lab 3 (Gateway)
- Tworzy **dodatkowy** Cognito User Pool (nie z CloudFormation). To normalne.
- Bearer token wazny ~1h. Przy dlugim labie moze wygasnac.

### Lab 4 (Runtime)
- Starter toolkit uzywa **CodeBuild** do buildu (nie lokalny Docker!). Docker Desktop nie jest wymagany.
- Platform mismatch warning na Apple Silicon — ignoruj.
- Runtime deploy: 1-5 minut. 
- **KOSZT**: Runtime jest billed per-second. Cleanup natychmiast po testach.

### Lab 5 (Evaluations)
- Wymaga aktywnego Runtime z Lab 4. Bez Runtime — blad.
- Wyniki w CloudWatch pojawiaja sie z opoznieniem 2-5 minut.
- `auto_create_execution_role=True` — starter toolkit sam tworzy IAM role.

### Lab 6 (Frontend)
- Wymaga aktywnego Runtime z Lab 4 i Cognito secret z Lab 3.
- Dziala na `http://localhost:8501`. Credentials: `testuser` / `MyPassword123!`
- Bug w `main.py`: `uuid.uuidv4()` — powinno byc `str(uuid.uuid4())`. Napraw recznie jesli wyrzuci blad.
- Lab opcjonalny — pokaz w trybie demo jesli brak czasu na warsztacie.

### Lab 8 (Payments)
- **NIE jest hands-on** — wymaga Coinbase/Stripe konta, faucet funding, delegated signing. Setup ~45 min per osoba.
- Pokaz jako demo/overview. Uczestnicy moga zrobic sami w domu.
- Preview — może nie byc dostepne na kazdym koncie.

### Lab 7 (Harness)
- Standalone — nie zalezy od Labs 1-6. Mozna odpalic osobno.
- Wymaga model access: **Claude Haiku 4.5** (lub zmien na Nova Lite w skrypcie).
- Harness sam sie czyści (delete w skrypcie). Nic nie zostaje po labie.
- IAM role `HarnessExecutionRole` — idempotentna, usuwana na koncu.

### DuckDuckGo
- `web_search` tool uzywa `ddgs` library. Rate-limited agresywnie. Jesli 15 osob jednoczesnie — beda bledy. Nie blokuje reszty.

### IAM
- Workshop wymaga broad permissions: `bedrock-agentcore:*`, `iam:CreateRole/PassRole`, `ecr:*`, `cloudformation:*`.
- Konta korporacyjne z permission boundaries prawdopodobnie nie dzialaja. Uzyj osobistych kont.

---

## Pomoc

Jesli cos nie dziala:
1. Sprawdz `aws sts get-caller-identity` — credentials OK?
2. Sprawdz `echo $AWS_REGION` — region sie zgadza?
3. Sprawdz `.venv` aktywne — `which python` powinno wskazywac na `.venv/`
4. Sprawdz SSM parametry — `bash scripts/list_ssm_parameters.sh`
