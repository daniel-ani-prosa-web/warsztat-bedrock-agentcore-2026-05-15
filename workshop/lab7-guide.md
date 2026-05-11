# Lab 7: AgentCore Harness — Agent w jednym API call

**Czas**: ~5-10 minut  
**Koszt**: ~$0.05 (pojedyncze invocations)  
**Wymaga**: Tylko AWS credentials. **NIE zalezy od Labs 1-6.**

## Czym jest Harness?

Harness pozwala odpalic agenta **jednym API callem** — bez frameworkow, bez Dockera, bez deployu. Podajesz model + prompt + tools i AWS uruchamia agenta w izolowanym Firecracker microVM.

Agent ma domyslnie dostepne narzedzia:
- `file_operations` — tworzenie/odczyt plikow na VM
- `shell` — wykonywanie komend na VM

Kazda sesja ma wlasny izolowany VM. Pliki stworzone w jednej sesji sa dostepne dopoki sesja zyje.

## Architektura

```
Twoj komputer (boto3)
    │
    ├── create_harness()     → Control Plane
    ├── invoke_harness()     → Data Plane → Firecracker microVM
    │                                         ├── LLM (Claude/Nova)
    │                                         ├── file_operations tool
    │                                         └── shell tool
    ├── invoke_agent_runtime_command()  → exec on VM
    └── delete_harness()     → Control Plane
```

## Krok 1: Model access

Harness uzywa **Claude Haiku 4.5** (default w tym labie). Upewnij sie ze jest wlaczony:
AWS Console → Bedrock → Model Access → Enable **Claude 4.5 Haiku**

Mozna tez uzyc Nova Lite — zmien `modelId` w skrypcie na `global.amazon.nova-2-lite-v1:0`.

## Krok 2: Instalacja

```bash
cd 11-AgentCore-harness
source ../09-AgentCore-E2E/strands-agents/.venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1
```

Dependencies: tylko `boto3` (juz zainstalowany).

## Krok 3: Uruchom

```bash
python /path/to/workshop/lab7-harness.py
```

## Co robi skrypt

| Krok | Co sie dzieje | Czas |
|------|---------------|------|
| 1 | Tworzy IAM role `HarnessExecutionRole` (idempotentne) | ~10s (propagation) |
| 2 | `create_harness()` — tworzy agenta, czeka na READY | ~10-30s |
| 3 | `invoke_harness()` — wysyla prompt, agent pisze plik na VM | ~10-20s |
| 4 | `invoke_agent_runtime_command()` — exec `ls`, `cat` na VM | ~5s |
| 5 | `delete_harness()` + delete IAM role | ~5s |

## Co zobaczysz

1. **Streaming response** — agent odpowiada na pytanie
2. **Tool calls** — `[Tool: file_operations]` gdy agent tworzy plik
3. **VM commands** — `pwd`, `ls`, `cat seattle.md` — widzisz pliki stworzone przez agenta
4. **Auto-cleanup** — harness i role usuwane na koncu

## Roznice vs Runtime (Lab 4)

| | Harness | Runtime |
|--|---------|---------|
| Setup | 0 — jedno API call | Dockerfile, ECR, deploy |
| Czas do pierwszego invoke | ~30s | ~10-15 min |
| Izolacja | Firecracker microVM per sesja | Container |
| Persistence | Sesja zyje dopoki nie usuniesz | Endpoint stale aktywny |
| Koszt | Per-invocation | Per-second while READY |
| Use case | Prototypowanie, eksperymenty | Produkcja, frontend |

## Typowe bledy

| Blad | Przyczyna | Rozwiazanie |
|------|-----------|-------------|
| `AccessDeniedException` on InvokeModel | Brak model access | Enable Claude Haiku 4.5 w Bedrock |
| Harness stuck in CREATING | IAM role nie propagated | Czekaj dluzej lub sprobuj ponownie |
| `NoSuchEntityException` on role | Juz wyczyszczone | Ignoruj |

## Eksploracja w konsoli

Bedrock → AgentCore → Harness — zobaczysz harness (jesli nie zdazyl sie usunac).
Harness jest efemeryczny — po `delete_harness()` znika.

## Nastepny krok

→ [Lab 8: Payments](lab8-guide.md) (opcjonalny)  
→ [Cleanup](cleanup-guide.md) (jesli pomijasz Lab 8)
