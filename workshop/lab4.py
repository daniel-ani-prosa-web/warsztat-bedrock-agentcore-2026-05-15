"""
Lab 4: Deploy to Production with AgentCore Runtime
====================================================
Builds Docker image, pushes to ECR, deploys agent to AgentCore Runtime.
Requires Docker running locally.
Run from strands-agents/ directory: python ../../workshop/lab4.py
"""

import os
import sys
import time
import uuid

STRANDS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "09-AgentCore-E2E", "strands-agents"
)
sys.path.insert(0, os.path.abspath(STRANDS_DIR))
os.chdir(STRANDS_DIR)

import boto3
from bedrock_agentcore_starter_toolkit import Runtime
from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
from bedrock_agentcore.memory.constants import StrategyType
from lab_helpers.utils import (
    create_agentcore_runtime_execution_role,
    get_ssm_parameter,
    get_or_create_cognito_pool,
    put_ssm_parameter,
)
from lab_helpers.lab2_memory import ACTOR_ID

boto_session = boto3.Session()
REGION = boto_session.region_name

print(f"Region: {REGION}")
print(f"Working directory: {os.getcwd()}")

# ---------------------------------------------------------------------------
# Step 1: Ensure Memory exists
# ---------------------------------------------------------------------------
print("\n--- Step 1: Ensuring AgentCore Memory exists ---")

memory_manager = MemoryManager(region_name=REGION)
memory = memory_manager.get_or_create_memory(
    name="CustomerSupportMemory",
    strategies=[
        {
            StrategyType.USER_PREFERENCE.value: {
                "name": "CustomerPreferences",
                "description": "Captures customer preferences and behavior",
                "namespaces": ["support/customer/{actorId}/preferences/"],
            }
        },
        {
            StrategyType.SEMANTIC.value: {
                "name": "CustomerSupportSemantic",
                "description": "Stores facts from conversations",
                "namespaces": ["support/customer/{actorId}/semantic/"],
            }
        },
    ],
)
memory_id = memory["id"]
print(f"Memory ID: {memory_id}")

# ---------------------------------------------------------------------------
# Step 2: Write runtime entrypoint (lab4_runtime.py already in lab_helpers)
# ---------------------------------------------------------------------------
print("\n--- Step 2: Runtime entrypoint already at lab_helpers/lab4_runtime.py ---")

# ---------------------------------------------------------------------------
# Step 3: Create IAM execution role
# ---------------------------------------------------------------------------
print("\n--- Step 3: Creating IAM execution role ---")

execution_role_arn = create_agentcore_runtime_execution_role()
print(f"Execution role: {execution_role_arn}")

# ---------------------------------------------------------------------------
# Step 4: Get Cognito token
# ---------------------------------------------------------------------------
print("\n--- Step 4: Getting Cognito access token ---")

access_token = get_or_create_cognito_pool(refresh_token=True)
print("Bearer token obtained")

# ---------------------------------------------------------------------------
# Step 5: Configure Runtime deployment
# ---------------------------------------------------------------------------
print("\n--- Step 5: Configuring Runtime deployment ---")
print("This generates Dockerfile and .bedrock_agentcore.yaml")

agentcore_runtime = Runtime()

response = agentcore_runtime.configure(
    entrypoint="lab_helpers/lab4_runtime.py",
    execution_role=execution_role_arn,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=REGION,
    agent_name="customer_support_agent",
    authorizer_configuration={
        "customJWTAuthorizer": {
            "allowedClients": [
                get_ssm_parameter("/app/customersupport/agentcore/client_id")
            ],
            "discoveryUrl": get_ssm_parameter(
                "/app/customersupport/agentcore/cognito_discovery_url"
            ),
        }
    },
    request_header_configuration={
        "requestHeaderAllowlist": [
            "Authorization",
            "X-Amzn-Bedrock-AgentCore-Runtime-Custom-H1",
        ]
    },
)
print(f"Configuration completed: {response}")

# ---------------------------------------------------------------------------
# Step 6: Launch (Docker build + ECR push + Runtime deploy)
# ---------------------------------------------------------------------------
print("\n--- Step 6: Launching to AgentCore Runtime ---")
print("This builds Docker image, pushes to ECR, and deploys to Runtime.")
print("Expect platform mismatch warning on Apple Silicon — safe to ignore.")
print("This step takes 5-10 minutes...")

launch_result = agentcore_runtime.launch(env_vars={"MEMORY_ID": memory_id})
print(f"Agent ARN: {launch_result.agent_arn}")

put_ssm_parameter("/app/customersupport/agentcore/runtime_arn", launch_result.agent_arn)

# ---------------------------------------------------------------------------
# Step 7: Wait for deployment
# ---------------------------------------------------------------------------
print("\n--- Step 7: Waiting for deployment to complete ---")

status_response = agentcore_runtime.status()
status = status_response.endpoint["status"]
end_statuses = {"READY", "CREATE_FAILED", "DELETE_FAILED", "UPDATE_FAILED"}

while status not in end_statuses:
    print(f"  Status: {status}")
    time.sleep(10)
    status_response = agentcore_runtime.status()
    status = status_response.endpoint["status"]

print(f"Final status: {status}")

if status != "READY":
    print(f"ERROR: Deployment failed with status {status}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 8: Test the deployed agent
# ---------------------------------------------------------------------------
print("\n--- Step 8: Testing deployed agent ---")

runtime_id = launch_result.agent_arn.split(":")[-1].split("/")[-1]
print(f"Runtime ID: {runtime_id}")

session_id = str(uuid.uuid4())

test_queries = [
    "List all of your tools",
    "Tell me about the return policy for laptops",
    "I have a Gaming Console Pro, warranty serial number is MNO33333333. Check my warranty.",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}: {query}")
    print("=" * 60)
    response = agentcore_runtime.invoke(
        {"prompt": query, "actor_id": ACTOR_ID},
        bearer_token=access_token["bearer_token"],
        session_id=session_id,
    )
    print(response["response"].replace("\\n", "\n"))

print("\n--- Lab 4 Complete ---")
print(f"Agent ARN: {launch_result.agent_arn}")
print(f"Runtime ID: {runtime_id}")
print("SSM parameter: /app/customersupport/agentcore/runtime_arn")
print("\nWARNING: Runtime is now active and billing. Run cleanup when done!")
