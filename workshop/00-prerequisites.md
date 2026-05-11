# Krok 0: Przygotowanie środowiska

Zrób to **przed warsztatem**. Na warsztacie nie będzie czasu na instalacje.

---

## 1. Konto AWS

Potrzebujesz **osobistego konta AWS** z admin access (lub bliskim). Konta korporacyjne z permission boundaries prawdopodobnie nie zadziałają — workshop wymaga `bedrock-agentcore:*`, `iam:CreateRole`, `ecr:*`, `cloudformation:*`.

Jeśli nie masz konta: [aws.amazon.com/free](https://aws.amazon.com/free/) — darmowy tier wystarczy, ale workshop generuje koszty ~$3-10.

---

## 2. Zainstaluj AWS CLI

### macOS

```bash
brew install awscli
```

Lub oficjalny installer:
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### Windows

Pobierz: [https://awscli.amazonaws.com/AWSCLIV2.msi](https://awscli.amazonaws.com/AWSCLIV2.msi)

### Linux

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Weryfikacja

```bash
aws --version
# aws-cli/2.x.x ...
```

---

## 3. Skonfiguruj AWS credentials

### Krok 1: Stwórz IAM usera (jeśli nie masz)

1. Zaloguj się do **AWS Console** jako root lub admin
2. Wyszukaj **IAM** → kliknij
3. Lewy panel → **Users** → **Create user**
4. Username: `workshop-user` (lub dowolna nazwa)
5. **Next** → **Attach policies directly** → zaznacz **AdministratorAccess**
6. **Next** → **Create user**

### Krok 2: Wygeneruj Access Keys

1. Kliknij na swojego usera (np. `workshop-user`)
2. Tab **Security credentials**
3. Sekcja **Access keys** → **Create access key**
4. Wybierz **Command Line Interface (CLI)**
5. Zaznacz checkbox "I understand..." na dole → **Next** → **Create access key**
6. **SKOPIUJ OBA KLUCZE** — pojawią się tylko raz!
   - **Access Key ID** — zaczyna się od `AKIA...`
   - **Secret Access Key** — długi ciąg znaków

> Możesz też kliknąć **Download .csv file** jako backup.

### Krok 3: Skonfiguruj w terminalu

```bash
aws configure --profile workshop
```

Podaj:
```
AWS Access Key ID: AKIA...........
AWS Secret Access Key: xxxxxxxxxxxxxxxxxxxxxxxx
Default region name: us-east-1
Default output format: json
```

### Weryfikacja credentials

```bash
export AWS_PROFILE=workshop
aws sts get-caller-identity
```

Powinno zwrócić:
```json
{
    "UserId": "AIDA...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/twoj-user"
}
```

Jeśli widzisz błąd `Unable to locate credentials` — powtórz krok 3.

---

## 4. Wybierz region

Workshop działa w regionach gdzie dostępny jest Amazon Bedrock AgentCore. Zalecane:

| Region | Kod |
|--------|-----|
| US East (N. Virginia) | `us-east-1` |
| US West (Oregon) | `us-west-2` |
| Europe (Frankfurt) | `eu-central-1` |

Ustaw region w terminalu:

```bash
export AWS_REGION=us-east-1
```

> **Ważne**: Używaj tego samego regionu we wszystkich komendach. Zmiana regionu w trakcie warsztatu = problemy.

---

## 5. Bedrock Model Access

Modele Amazon Bedrock (Nova Lite, Claude) **aktywują się automatycznie** przy pierwszym wywołaniu — nie trzeba nic włączać ręcznie. Strona "Model access" w konsoli została wycofana.

Jedyny wyjątek: modele Anthropic (Claude) mogą wymagać jednorazowego podania use case przy pierwszym użyciu. Jeśli Lab 7 (Harness, Claude Haiku) zwróci `AccessDeniedException`, wejdź w Bedrock → Model catalog → Claude 4.5 Haiku → spróbuj otworzyć w playground — poprosi o use case form.

---

## 6. Zainstaluj Python 3.10-3.13

**Python 3.14 NIE działa** — `strands-agents` nie ma buildu dla 3.14.

### Sprawdź wersję

```bash
python3 --version
```

Jeśli masz 3.10-3.13 — OK. Jeśli 3.14 lub starszą:

### macOS

```bash
brew install python@3.13
```

### Windows

Pobierz 3.13 z [python.org/downloads](https://www.python.org/downloads/)

### Linux

```bash
sudo apt install python3.13 python3.13-venv  # Ubuntu/Debian
```

---

## 7. Zainstaluj uv (opcjonalne, ale zalecane)

`uv` to szybki package manager dla Pythona. Znacznie szybszy niż `pip`.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Lub via pip
pip install uv
```

---

## 8. Zainstaluj Git

Prawdopodobnie masz. Sprawdź:

```bash
git --version
```

Jeśli nie: [git-scm.com/downloads](https://git-scm.com/downloads)

---

## Checklist przed warsztatem

Uruchom po kolei i sprawdź czy wszystko OK:

```bash
# 1. AWS CLI
aws --version

# 2. Credentials
export AWS_PROFILE=workshop
export AWS_REGION=us-east-1
aws sts get-caller-identity

# 3. Python
python3 --version  # 3.10-3.13

# 4. Git
git --version
```

Jeśli wszystkie 4 komendy przeszły bez błędu — jesteś gotowy.

---

## Alternatywa: AWS CloudShell

Jeśli nie chcesz instalować niczego lokalnie, możesz użyć **AWS CloudShell** w konsoli AWS:

1. AWS Console → ikona terminala w prawym górnym rogu (lub wyszukaj "CloudShell")
2. Ma pre-installed: AWS CLI, Python, Git, zip
3. Credentials są automatyczne (z konta w którym jesteś zalogowany)
4. Region dziedziczony z konsoli

Ograniczenia:
- Brak Docker Desktop (ale Lab 4 używa CodeBuild server-side)
- Sesja timeout po 20 min nieaktywności
- 1 GB persistent storage

---

## Problemy?

| Problem | Rozwiązanie |
|---------|-------------|
| `Unable to locate credentials` | `export AWS_PROFILE=workshop` i sprawdź `aws configure list` |
| `An error occurred (AccessDenied)` | Twój user/role nie ma wystarczających uprawnień. Użyj admin access. |
| `Could not connect to endpoint` | Sprawdź `echo $AWS_REGION` — musi być ustawiony |
| Python 3.14 | `brew install python@3.13` lub `uv venv --python 3.13` |
| `command not found: aws` | Zainstaluj AWS CLI (krok 2) |
