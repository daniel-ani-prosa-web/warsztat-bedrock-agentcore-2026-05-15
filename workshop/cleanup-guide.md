# Cleanup: Usuniecie zasobow

**OBOWIAZKOWE** — Runtime kosztuje dopoki dziala!

## Krok 1: Usun zasoby AgentCore

```bash
cd 09-AgentCore-E2E/strands-agents
source .venv/bin/activate
export AWS_PROFILE=personal AWS_REGION=us-east-1

python /path/to/workshop/cleanup.py
```

Skrypt usunie:
- AgentCore Evaluation config (z Lab 5)
- AgentCore Memory
- AgentCore Runtime + ECR repo
- Policy Engine (jesli tworzony)
- Gateway + targety
- IAM execution role
- Cognito User Pool (ten z Lab 3, nie z CloudFormation)
- Secrets Manager secret
- CloudWatch log groups
- Lokalne pliki (Dockerfile, .bedrock_agentcore.yaml, etc.)

## Krok 2: Usun CloudFormation stacks

```bash
bash scripts/cleanup.sh
```

Lub w konsoli AWS:
1. CloudFormation → Delete `CustomerSupportStackCognito`
2. CloudFormation → Delete `CustomerSupportStackInfra`
3. S3 → Empty + Delete bucket `customersupport112-{ACCOUNT_ID}-{REGION}`

## Weryfikacja

```bash
# Sprawdz czy nie ma zadnych zasobow
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE --query 'StackSummaries[?contains(StackName, `CustomerSupport`)].StackName' --output text

# Sprawdz czy Runtime usuniety
aws bedrock-agentcore-control list-agent-runtimes --query 'agentRuntimes[].agentRuntimeId' --output text
```
