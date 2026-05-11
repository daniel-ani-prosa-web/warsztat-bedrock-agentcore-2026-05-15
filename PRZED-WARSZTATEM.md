# Warsztaty AWS UG Wrocław — piątek 15.05.2026

Cześć! W piątek robimy hands-on warsztaty. Żebyśmy nie tracili czasu na setup, przygotuj poniższe rzeczy wcześniej.

## Co potrzebujesz

1. **Konto AWS** — osobiste, z uprawnieniami admina. Konta firmowe z ograniczeniami mogą nie działać. Jeśli nie masz: [aws.amazon.com/free](https://aws.amazon.com/free/)

2. **AWS CLI** — zainstalowany i skonfigurowany z Access Key ID + Secret Access Key. Instrukcja: [workshop/00-prerequisites.md](workshop/00-prerequisites.md)

3. **Python 3.10-3.13** — uwaga: 3.14 nie działa

4. **Git**

## Sprawdź czy działa

```bash
export AWS_PROFILE=twoj-profil
export AWS_REGION=us-east-1

aws sts get-caller-identity
python3 --version
```

Jeśli `get-caller-identity` zwraca JSON z Twoim kontem, a Python jest 3.10-3.13 — jesteś gotowy.

Do zobaczenia w piątek!
