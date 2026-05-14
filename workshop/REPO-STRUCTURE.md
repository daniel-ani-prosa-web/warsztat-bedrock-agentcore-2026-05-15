# Struktura repo

To repo ma jeden główny punkt wejścia dla uczestników: `workshop/WORKSHOP.md`.

Katalogi `09-AgentCore-E2E/` i `11-AgentCore-harness/` są katalogami roboczymi z kodem sampli AWS. Wchodzisz do nich tylko wtedy, gdy guide mówi, żeby tam odpalić komendę.

## Katalogi

| Katalog | Rola |
|---------|------|
| `workshop/` | Guide'y, uproszczone skrypty labów, cleanup i agenda warsztatu |
| `09-AgentCore-E2E/strands-agents/` | Katalog roboczy dla setupu oraz Labs 1-6 |
| `11-AgentCore-harness/` | Katalog roboczy dla Lab 7 Harness |
| `09-AgentCore-E2E/strands-agents/lab_helpers/` | Kod pomocniczy używany przez laby i frontend |
| `11-AgentCore-harness/00-getting-started/` | Notebook/README źródłowego sampla Harness |

## Gdzie być w terminalu

### Setup i Labs 1-6

```bash
cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1
```

Uruchamianie labów:

```bash
python ../../workshop/lab1.py
python ../../workshop/lab2.py
python ../../workshop/lab3.py
python ../../workshop/lab4.py
python ../../workshop/lab5.py
```

Lab 6 frontend:

```bash
uv pip install -r lab_helpers/lab5_frontend/requirements.txt
cd lab_helpers/lab5_frontend
python -m streamlit run main.py
```

### Lab 7 Harness

Lab 7 jest standalone i używa innego katalogu roboczego:

```bash
cd 11-AgentCore-harness
source ../09-AgentCore-E2E/strands-agents/.venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1 AWS_DEFAULT_REGION=us-east-1
python ../workshop/lab7-harness.py
```

### Cleanup

Cleanup wraca do katalogu Labs 1-6:

```bash
cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1
python ../../workshop/cleanup.py
bash scripts/cleanup.sh
```

`scripts/cleanup.sh` zapyta o potwierdzenie usunięcia stacków i bucketu. W dry-runie automatycznym:

```bash
printf 'y\ny\n' | bash scripts/cleanup.sh
```

## Czego nie robić

- Nie przenoś katalogów `09-AgentCore-E2E/` ani `11-AgentCore-harness/`; notebooki i helpery używają relatywnych ścieżek.
- Nie startuj od notebooków, jeśli idziesz ścieżką CLI z `workshop/WORKSHOP.md`.
- Nie rób cleanupu przed Lab 6, bo frontend wymaga aktywnego Runtime z Lab 4.
