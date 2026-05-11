# Agenda — Warsztat Amazon Bedrock AgentCore

**AWS UG Wrocław, 15 maja 2026**  
**Czas**: ~2.5-3h  
**Uczestnicy**: 15 osób

---

## Timeline

| Czas | Co | Uwagi |
|------|-----|-------|
| 0:00 | **Intro + setup check** | `bash check-ready.sh`, naprawianie problemów |
| 0:15 | **prereq.sh** | Odpalają, czekają ~10 min. W tym czasie opowiadasz o AgentCore |
| 0:25 | **Lab 1** — Agent prototype | Pierwszy "wow" — agent odpowiada z toolami |
| 0:40 | **Lab 2** — Memory | Agent pamięta klienta. Pokaż extracted memories |
| 1:00 | **Lab 3** — Gateway + Identity | MCP, Cognito JWT, remote tools |
| 1:20 | *Przerwa 10 min* | |
| 1:30 | **Lab 4** — Runtime deploy | Deploy do produkcji. **Pokaż CloudWatch traces!** |
| 2:00 | **Lab 5** — Evaluations | Online eval config + 5 test queries |
| 2:15 | **Lab 6** — Frontend | Streamlit demo (opcjonalne, można pokazać na ekranie) |
| 2:25 | **Lab 7** — Harness | Bonus: agent w jednym API call |
| 2:35 | **Payments** — opowiadanie | 10 min overview, architektura, x402 |
| 2:45 | **Cleanup** | Wszyscy odpalają cleanup.py + cleanup.sh |
| 2:55 | **Q&A** | |

## Bufory czasowe

- **Lab 4** (Runtime) jest najdłuższy — CodeBuild może trwać 5-10 min. Wykorzystaj ten czas na opowiadanie o observability.
- **Lab 6** (Frontend) — jeśli brak czasu, pokaż na swoim ekranie zamiast kazać wszystkim odpalać.
- **Lab 7** (Harness) — jeśli brak czasu, pomiń. Jest standalone.

## Punkty gdzie ludzie utkną

| Moment | Problem | Rozwiązanie |
|--------|---------|-------------|
| Setup | `Unable to locate credentials` | Nie ustawili `AWS_PROFILE` |
| Setup | Python 3.14 | `uv venv .venv --python 3.13` |
| prereq.sh | Przerywają Ctrl+C | Nie szkodzi, odpalają ponownie (idempotentne) |
| Lab 1 | `web_search` rate limit | 15 osób = DDGS limit. Ignorować, reszta działa |
| Lab 3 | Cognito token expired | Odpalić ponownie |
| Lab 4 | Build trwa za długo | Normalne, czekać |
| Cleanup | Zapominają odpalić | **PRZYPOMINAJ GŁOŚNO** — Runtime kosztuje |

## DuckDuckGo — 15 osób

`web_search` tool używa DDGS (DuckDuckGo). 15 osób na tym samym WiFi/NAT = rate limit pewny.

**Nie blokuje warsztatu** — agent ma 3 inne toole. Jeśli `web_search` zwróci błąd, agent powie "nie mogłem wyszukać" i użyje innych toolów.

Uprzedź uczestników: "web search może nie działać gdy wszyscy odpytujemy jednocześnie — to normalne, reszta agenta działa".

## Cleanup reminder

Na 15 minut przed końcem:
1. Powiedz głośno: "Teraz wszyscy odpalacie cleanup"
2. Wyświetl na ekranie komendy
3. Poczekaj aż wszyscy potwierdzą
4. **Sprawdź sam** czy nikt nie zostawił Runtime
