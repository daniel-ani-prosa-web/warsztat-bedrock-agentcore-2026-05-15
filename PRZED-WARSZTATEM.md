# Warsztaty Amazon Bedrock AgentCore — AWS UG Wrocław, 15.05.2026

Cześć! W piątek budujemy agenta AI na AWS od zera do produkcji. Żebyśmy nie tracili czasu na instalacje, przygotuj się wcześniej.

## Co będziemy robić

Krok po kroku zbudujemy Customer Support Agenta który:
- Odpowiada na pytania klientów, szuka w bazie wiedzy, sprawdza gwarancje
- Pamięta klientów między sesjami (managed memory)
- Ma centralne narzędzia przez API (Gateway + auth)
- Jest zdeployowany do produkcji z monitoringiem
- Ma frontend z czatem
- Bonus: agent w jednym API call (zero konfiguracji)

Wszystko na AWS, z kodem w Pythonie. Koszt: ~$3-10 (czyścimy na koniec).

## Co potrzebujesz

### Obowiązkowe

- [ ] **Konto AWS** — osobiste z admin access. Konta firmowe z ograniczeniami mogą nie działać.
- [ ] **AWS CLI** — zainstalowany i skonfigurowany z credentials ([instrukcja](workshop/00-prerequisites.md))
- [ ] **Python 3.10-3.13** — uwaga: Python 3.14 **nie działa** z bibliotekami które używamy
- [ ] **Git** — do sklonowania repo

### Opcjonalne

- [ ] `uv` — szybszy package manager (`pip install uv`), ale zwykły `pip` też OK

### NIE potrzebujesz

- ~~Docker~~ — build jest server-side w AWS
- ~~Jupyter~~ — nie używamy notebooków
- ~~Konta Coinbase/Stripe~~ — to tylko opowiadanie

## Sprawdź czy wszystko działa

```bash
git clone https://github.com/daniel-ani-prosa-web/warsztat-bedrock-agentcore-2026-05-15.git
cd warsztat-bedrock-agentcore-2026-05-15

export AWS_PROFILE=twoj-profil
export AWS_REGION=us-east-1
bash check-ready.sh
```

Powinno pokazać same `[OK]`. Jeśli coś jest `[FAIL]` — szczegóły jak naprawić są w `workshop/00-prerequisites.md`.

## Jeśli nie masz AWS CLI / nie chcesz instalować lokalnie

Możesz użyć **AWS CloudShell** w konsoli AWS (ikona terminala w prawym górnym rogu). Ma wbudowane: AWS CLI, Python, Git. Credentials automatyczne.

## Na warsztacie

Przynieś laptopa z terminalem. Będziemy odpalać skrypty Python z CLI — żadnych notebooków, żadnego klikania w konsoli (chociaż pokażemy co się dzieje w konsoli AWS po każdym kroku).

Do zobaczenia w piątek!
