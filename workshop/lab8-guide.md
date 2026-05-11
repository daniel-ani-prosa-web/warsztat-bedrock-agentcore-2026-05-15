# Lab 8: AgentCore Payments — Overview (demo/take-home)

**Typ**: Prezentacja/demo, NIE hands-on  
**Czas**: ~10 minut (pokaz)  
**Koszt**: $0 (nic nie deployujemy)  
**Dlaczego nie hands-on**: Wymaga Coinbase CDP lub Stripe/Privy konta, manual funding z fauceta, delegated signing w przegladarce. Setup trwa ~45 min per osoba.

## Czym jest AgentCore Payments?

Managed service do **mikrotransakcji dla agentow AI**. Agent moze automatycznie placic za:
- Platne API (x402 protocol)
- Platne MCP toole (Coinbase Bazaar — 10 000+ narzedzi)
- Paywall content (strony z paywallem)

Platnosci sa w **USDC (stablecoin)** na testnet (Base Sepolia / Solana Devnet). Kwoty rzedu $0.01-$0.10 per call.

## Architektura

```
Developer (ControlPlaneRole)
    │
    ├── CredentialProvider  ← klucze Coinbase/Stripe (encrypted)
    ├── PaymentManager      ← top-level config
    └── PaymentConnector    ← laczy Manager z Provider
                │
                ▼
Application Backend (ManagementRole)
    │
    ├── CreateInstrument    ← wallet (embedded crypto)
    └── CreateSession       ← budzet ($1.00, 60 min)
                │
                ▼
Agent Runtime (ProcessPaymentRole)
    │
    └── ProcessPayment      ← placi automatycznie przy x402
```

**Key design**: Role separation — kod ktory ustawia budzet (ManagementRole) NIE moze wykonac platnosci. Kod ktory placi (ProcessPaymentRole) NIE moze zmieniac budzetow.

## x402 Protocol Flow

```
Agent → GET /api/data
                ← 402 Payment Required
                   (price: $0.01 USDC, payTo: 0x...)

Agent → ProcessPayment(price, payTo)
                ← payment proof (signed tx)

Agent → GET /api/data + X-PAYMENT: proof
                ← 200 OK + data
```

## Resource Hierarchy

```
PaymentManager
  └── PaymentConnector (Coinbase CDP lub Stripe/Privy)
       └── PaymentInstrument (embedded wallet, per user)
            └── PaymentSession (budzet + czas)
```

## Co potrzeba do samodzielnego zrobienia (take-home)

### 1. Wallet provider

**Opcja A — Coinbase CDP** (latwiejsze):
1. Zaloz konto na [portal.cdp.coinbase.com](https://portal.cdp.coinbase.com/)
2. Stworz API key (API Key ID + Secret + Wallet Secret)
3. Zapisz do `.env`

**Opcja B — Stripe/Privy**:
1. Zaloz konto na [dashboard.privy.io](https://dashboard.privy.io/)
2. Stworz app, wygeneruj keys
3. Uruchom reference frontend (Node.js)
4. Zapisz do `.env`

### 2. Setup (Tutorial 00)

```bash
cd 01-tutorials/13-AgentCore-payments/00-getting-started/00-setup-agentcore-payments
cp .env.coinbase.sample .env  # lub .env.privy.sample
# Uzupelnij .env kluczami z kroku 1
jupyter notebook setup_agentcore_payments.ipynb
```

Tworzy: 4 IAM role, PaymentManager, Connector, Instrument (wallet), Session (budzet).

### 3. Funding

1. Skopiuj adres walleta z output
2. Idz na [faucet.circle.com](https://faucet.circle.com/) → Base Sepolia
3. Wklej adres, request 20 USDC (testnet, za darmo)
4. Deleguj signing w WalletHub (Coinbase) lub reference frontend (Privy)

### 4. Tutorial 01 — Agent z platnosami

```bash
cd ../01-agents-payments-and-limits
jupyter notebook strands_payment_agent.ipynb
```

Agent z Strands ktory automatycznie placi za x402 endpointy z budget enforcement.

## Dostepne tutoriale (w repo)

| # | Tutorial | Co robi |
|---|----------|---------|
| 00 | Setup | IAM, Manager, Connector, Wallet, Session |
| 01 | Payment limits | Agent placi z budzetem, rejection przy przekroczeniu |
| 02 | Deploy to Runtime | Payment agent na AgentCore Runtime |
| 03 | Wallet operations | Onboarding, funding, delegation, balance |
| 04 | Gateway + Bazaar | 10 000+ platnych MCP tooli via Gateway |
| 05 | Browser + payments | Agent przechodzi przez paywall w przegladarce |
| 06 | Multi-agent | Wielu agentow, osobne wallety, osobne budzety |

## Linki

- [Repo](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/01-tutorials/13-AgentCore-payments)
- [Dokumentacja](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments.html)
- [Blog post](https://aws.amazon.com/blogs/machine-learning/agents-that-transact-introducing-amazon-bedrock-agentcore-payments-built-with-coinbase-and-stripe/)
- [Coinbase Bazaar](https://www.coinbase.com/en-ca/blog/introducing-amazon-bedrock-agentcore-payments-powered-by-x402-and-coinbase)

## Bezpieczenstwo

- Wszystkie tutoriale uzywaja **testnet only** (Base Sepolia / Solana Devnet)
- USDC z fauceta nie ma wartosci
- Nigdy nie commituj `.env` ani private keys
- W produkcji: Secrets Manager, least-privilege IAM, VPC endpoints
