"""
Lab 3: Scale with Gateway and Identity
========================================
Creates AgentCore Gateway with Lambda target, Cognito auth, MCP client integration.
Optional: Cedar policy engine for fine-grained access control.
Run from strands-agents/ directory: python ../../workshop/lab3.py
"""

import json
import os
import sys
import time
import uuid

STRANDS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "09-AgentCore-E2E", "strands-agents"
)
sys.path.insert(0, os.path.abspath(STRANDS_DIR))

import boto3
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

from lab_helpers.utils import (
    get_or_create_cognito_pool,
    put_ssm_parameter,
    get_ssm_parameter,
    load_api_spec,
)
from lab_helpers.lab1_strands_agent import (
    get_product_info,
    get_return_policy,
    get_technical_support,
    SYSTEM_PROMPT,
    MODEL_ID,
)
from lab_helpers.lab2_memory import create_or_get_memory_resource
from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig,
    RetrievalConfig,
)
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)

sts_client = boto3.client("sts")
account_id = sts_client.get_caller_identity()["Account"]
REGION = boto3.session.Session().region_name

gateway_client = boto3.client("bedrock-agentcore-control", region_name=REGION)

print(f"Account: {account_id}  Region: {REGION}")

# ---------------------------------------------------------------------------
# Step 1: Cognito auth setup
# ---------------------------------------------------------------------------
print("\n--- Step 1: Setting up Cognito authentication ---")

cognito_config = get_or_create_cognito_pool(refresh_token=True)
print(f"Cognito Pool ID: {cognito_config['pool_id']}")
print(f"Bearer token obtained (expires in ~1h)")

auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"],
    }
}

# ---------------------------------------------------------------------------
# Step 2: Create AgentCore Gateway
# ---------------------------------------------------------------------------
print("\n--- Step 2: Creating AgentCore Gateway ---")

gateway_name = "customersupport-gw"

try:
    create_response = gateway_client.create_gateway(
        name=gateway_name,
        roleArn=get_ssm_parameter("/app/customersupport/agentcore/gateway_iam_role"),
        protocolType="MCP",
        authorizerType="CUSTOM_JWT",
        authorizerConfiguration=auth_config,
        description="Customer Support AgentCore Gateway",
    )
    gateway_id = create_response["gatewayId"]
    gateway = {
        "id": gateway_id,
        "name": gateway_name,
        "gateway_url": create_response["gatewayUrl"],
        "gateway_arn": create_response["gatewayArn"],
    }
    put_ssm_parameter("/app/customersupport/agentcore/gateway_id", gateway_id)
    put_ssm_parameter("/app/customersupport/agentcore/gateway_name", gateway_name)
    put_ssm_parameter("/app/customersupport/agentcore/gateway_arn", create_response["gatewayArn"])
    put_ssm_parameter("/app/customersupport/agentcore/gateway_url", create_response["gatewayUrl"])
    time.sleep(3)
    print(f"Gateway created: {gateway_id}")
except Exception:
    existing_gateway_id = get_ssm_parameter("/app/customersupport/agentcore/gateway_id")
    gateway_response = gateway_client.get_gateway(gatewayIdentifier=existing_gateway_id)
    gateway = {
        "id": existing_gateway_id,
        "name": gateway_response["name"],
        "gateway_url": gateway_response["gatewayUrl"],
        "gateway_arn": gateway_response["gatewayArn"],
    }
    gateway_id = gateway["id"]
    print(f"Using existing gateway: {gateway_id}")

print(f"Gateway URL: {gateway['gateway_url']}")

# ---------------------------------------------------------------------------
# Step 3: Add Lambda target
# ---------------------------------------------------------------------------
print("\n--- Step 3: Adding Lambda target to Gateway ---")

api_spec_file = os.path.join(STRANDS_DIR, "prerequisite", "lambda", "api_spec.json")
if not os.path.exists(api_spec_file):
    print(f"ERROR: API spec not found: {api_spec_file}")
    sys.exit(1)

api_spec = load_api_spec(api_spec_file)

try:
    lambda_target_config = {
        "mcp": {
            "lambda": {
                "lambdaArn": get_ssm_parameter("/app/customersupport/agentcore/lambda_arn"),
                "toolSchema": {"inlinePayload": api_spec},
            }
        }
    }
    credential_config = [{"credentialProviderType": "GATEWAY_IAM_ROLE"}]

    create_target_response = gateway_client.create_gateway_target(
        gatewayIdentifier=gateway_id,
        name="LambdaUsingSDK",
        description="Lambda Target using SDK",
        targetConfiguration=lambda_target_config,
        credentialProviderConfigurations=credential_config,
    )
    print(f"Target created: {create_target_response['targetId']}")
except Exception as e:
    print(f"Target may already exist: {e}")

# ---------------------------------------------------------------------------
# Step 4: Test MCP client connection
# ---------------------------------------------------------------------------
print("\n--- Step 4: Testing MCP client connection ---")
print(f"MCP URL: {gateway['gateway_url']}")

mcp_client = MCPClient(
    lambda: streamablehttp_client(
        gateway["gateway_url"],
        headers={"Authorization": f"Bearer {cognito_config['bearer_token']}"},
    )
)

with mcp_client:
    tools = mcp_client.list_tools_sync()
    print(f"Found {len(tools)} MCP tool(s):")
    for tool in tools:
        print(f"  - {tool.mcp_tool.name}: {tool.mcp_tool.description}")

# ---------------------------------------------------------------------------
# Step 5: Create agent with MCP + local tools + memory
# ---------------------------------------------------------------------------
print("\n--- Step 5: Creating agent with Gateway tools ---")

memory_id = create_or_get_memory_resource()
CUSTOMER_ID = "customer_001"
SESSION_ID = str(uuid.uuid4())

memory_config = AgentCoreMemoryConfig(
    memory_id=memory_id,
    session_id=SESSION_ID,
    actor_id=CUSTOMER_ID,
    retrieval_config={
        "support/customer/{actorId}/semantic/": RetrievalConfig(top_k=3, relevance_score=0.2),
        "support/customer/{actorId}/preferences/": RetrievalConfig(top_k=3, relevance_score=0.2),
    },
)

model = BedrockModel(model_id=MODEL_ID, temperature=0.3, region_name=REGION)


def create_agent(prompt):
    with mcp_client:
        all_tools = [
            get_product_info,
            get_return_policy,
            get_technical_support,
        ] + mcp_client.list_tools_sync()

        agent = Agent(
            model=model,
            tools=all_tools,
            system_prompt=SYSTEM_PROMPT,
            session_manager=AgentCoreMemorySessionManager(memory_config, REGION),
        )
        return agent(prompt)


# ---------------------------------------------------------------------------
# Step 6: Test agent with MCP tools
# ---------------------------------------------------------------------------
print("\n--- Step 6: Testing agent with MCP tools ---")

test_prompts = [
    "List all of your tools",
    "I have a Gaming Console Pro, I want to check my warranty status, serial number is MNO33333333.",
]

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}: {prompt}")
    print("=" * 60)
    try:
        response = create_agent(prompt)
    except Exception as e:
        print(f"Error: {e}")

# ---------------------------------------------------------------------------
# [OPTIONAL] Step 7: Cedar Policy Engine
# ---------------------------------------------------------------------------
ENABLE_POLICY_ENGINE = os.environ.get("ENABLE_POLICY_ENGINE", "false").lower() == "true"

if ENABLE_POLICY_ENGINE:
    print("\n--- [Optional] Step 7: Setting up Cedar Policy Engine ---")

    from bedrock_agentcore_starter_toolkit.operations.policy.client import PolicyClient
    from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient as GWToolkitClient

    policy_client = PolicyClient(region_name=REGION)

    engine = policy_client.create_or_get_policy_engine(
        name="customersupport_pe",
        description="Policy engine for customer support gateway",
    )
    engine_id = engine["policyEngineId"]
    put_ssm_parameter("/app/customersupport/agentcore/policy_engine_id", engine_id)
    print(f"Policy Engine: {engine_id}")

    allow_policy = {
        "cedar": {
            "statement": (
                f'permit(\n'
                f'    principal,\n'
                f'    action in [AgentCore::Action::"LambdaUsingSDK___check_warranty_status", '
                f'AgentCore::Action::"LambdaUsingSDK___web_search"],\n'
                f'    resource == AgentCore::Gateway::"{gateway["gateway_arn"]}"\n'
                f') when {{\n'
                f'    (principal.hasTag("username")) && \n'
                f'    ((principal.getTag("username")) == "testuser")\n'
                f'}};'
            )
        }
    }

    deny_web_search_policy = {
        "cedar": {
            "statement": (
                f'forbid(\n'
                f'    principal,\n'
                f'    action == AgentCore::Action::"LambdaUsingSDK___web_search",\n'
                f'    resource == AgentCore::Gateway::"{gateway["gateway_arn"]}"\n'
                f') when {{\n'
                f'    context.input has keywords &&\n'
                f'    context.input.keywords like "*iPhone 8*"\n'
                f'}};'
            )
        }
    }

    for name, definition, desc in [
        ("allow_policy", allow_policy, "Allow web_search and check_warranty_status"),
        ("deny_web_search", deny_web_search_policy, "Deny web_search for iPhone 8"),
    ]:
        try:
            policy_client.create_or_get_policy(
                policy_engine_id=engine_id, name=name, description=desc, definition=definition
            )
            print(f"  Policy ready: {name}")
        except Exception:
            cp = boto3.client("bedrock-agentcore-control", region_name=REGION)
            for p in cp.list_policies(policyEngineId=engine_id).get("policies", []):
                if p["name"] == name and p["status"] == "CREATE_FAILED":
                    cp.delete_policy(policyEngineId=engine_id, policyId=p["policyId"])
                    time.sleep(2)
            policy_client.create_or_get_policy(
                policy_engine_id=engine_id, name=name, description=desc,
                definition=definition, validation_mode="IGNORE_ALL_FINDINGS",
            )
            print(f"  Policy ready (IGNORE_ALL_FINDINGS): {name}")

    role_arn = get_ssm_parameter("/app/customersupport/agentcore/gateway_iam_role")
    role_name = role_arn.split("/")[-1]
    iam_client = boto3.client("iam")
    iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName="PolicyEngineAccess",
        PolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["bedrock-agentcore:*"],
                "Resource": [
                    f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:policy-engine/*",
                    f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:gateway/*",
                ],
            }],
        }),
    )
    print("  IAM role updated, waiting 10s for propagation...")
    time.sleep(10)

    gw_toolkit = GWToolkitClient(region_name=REGION)
    gw_toolkit.update_gateway_policy_engine(
        gateway_identifier=gateway["id"],
        policy_engine_arn=engine["policyEngineArn"],
        mode="ENFORCE",
    )
    print("  Policy Engine attached to Gateway in ENFORCE mode")

    print("\n  Testing policy enforcement...")
    policy_tests = [
        "Search the web for heating issues with Samsung Z Fold 7",
        "Search the internet for heating issues with iPhone 8",
    ]
    for i, prompt in enumerate(policy_tests, 1):
        print(f"\n  Policy Test {i}: {prompt}")
        try:
            response = create_agent(prompt)
        except Exception as e:
            print(f"  Error (expected for denied): {e}")
else:
    print("\n--- [Optional] Policy Engine skipped (set ENABLE_POLICY_ENGINE=true to enable) ---")

print("\n--- Lab 3 Complete ---")
print(f"Resources created: Gateway '{gateway_name}' (ID: {gateway_id})")
print(f"Gateway URL: {gateway['gateway_url']}")
print("SSM params: gateway_id, gateway_name, gateway_arn, gateway_url")
