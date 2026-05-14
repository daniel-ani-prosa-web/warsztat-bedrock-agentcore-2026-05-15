"""
Lab 5: Evaluate Agent Performance (Online Evaluations)
=======================================================
Configures continuous online evaluation for the deployed agent.
Requires Runtime from Lab 4 to be active.
Run from strands-agents/ directory: python ../../workshop/lab5.py
"""

import json
import os
import sys
import uuid

STRANDS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "09-AgentCore-E2E", "strands-agents"
)
sys.path.insert(0, os.path.abspath(STRANDS_DIR))
os.chdir(STRANDS_DIR)

from pathlib import Path
from boto3.session import Session
from bedrock_agentcore_starter_toolkit import Evaluation, Runtime
from lab_helpers.utils import get_ssm_parameter, get_or_create_cognito_pool

boto_session = Session()
region = boto_session.region_name
print(f"Region: {region}")

# ---------------------------------------------------------------------------
# Step 1: Retrieve agent info from Lab 4
# ---------------------------------------------------------------------------
print("\n--- Step 1: Retrieving agent info from Lab 4 ---")

try:
    agent_arn = get_ssm_parameter("/app/customersupport/agentcore/runtime_arn")
    agent_id = agent_arn.split(":")[-1].split("/")[-1]
    print(f"Agent ID: {agent_id}")
    print(f"Agent ARN: {agent_arn}")
except Exception as e:
    print(f"ERROR: Missing agent from Lab 4. Run lab4.py first.\n{e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 2: Create online evaluation config
# ---------------------------------------------------------------------------
print("\n--- Step 2: Creating online evaluation configuration ---")
print("Evaluators: GoalSuccessRate, Correctness, ToolSelectionAccuracy")
print("Sampling rate: 100% (demo only, use 10-20% in production)")

eval_client = Evaluation(region=region)

response = eval_client.create_online_config(
    agent_id=agent_id,
    config_name="customer_support_agent_eval",
    sampling_rate=100,
    evaluator_list=[
        "Builtin.GoalSuccessRate",
        "Builtin.Correctness",
        "Builtin.ToolSelectionAccuracy",
    ],
    config_description="Customer support agent online evaluation",
    auto_create_execution_role=True,
)

config_id = response["onlineEvaluationConfigId"]
print(f"Configuration ID: {config_id}")

# ---------------------------------------------------------------------------
# Step 3: Verify config
# ---------------------------------------------------------------------------
print("\n--- Step 3: Verifying configuration ---")

config_details = eval_client.get_online_config(config_id=config_id)
print(json.dumps(config_details, indent=2, default=str))

# ---------------------------------------------------------------------------
# Step 4: Generate test interactions
# ---------------------------------------------------------------------------
print("\n--- Step 4: Generating test interactions for evaluation ---")

access_token = get_or_create_cognito_pool(refresh_token=True)

runtime_client = Runtime()
runtime_client._config_path = Path.cwd() / ".bedrock_agentcore.yaml"

test_scenarios = [
    ("Product info", "I need information about the Gaming Console Pro. What are its specifications and price?"),
    ("Tech support", "My laptop won't start up. Can you help me troubleshoot this issue?"),
    ("Return policy", "I bought a smartphone last week but it's not working properly. What's your return policy?"),
    ("Multi-tool", "I need help with my Gaming Console Pro. First, can you tell me about its warranty? Then I need technical support for connection issues."),
    ("Capabilities", "What kind of support can you provide? List all your available tools and capabilities."),
]

for name, prompt in test_scenarios:
    session_id = str(uuid.uuid4())
    print(f"\n  [{name}]: {prompt[:60]}...")
    try:
        resp = runtime_client.invoke(
            payload={"prompt": prompt},
            session_id=session_id,
            bearer_token=access_token["bearer_token"],
        )
        answer = resp.get("response", "")
        print(f"  Response: {answer[:100]}...")
    except Exception as e:
        print(f"  Error: {e}")

print("\n--- Lab 5 Complete ---")
print(f"Evaluation config ID: {config_id}")
print(f"\nView results in CloudWatch:")
print(f"  https://console.aws.amazon.com/cloudwatch/home?region={region}#gen-ai-observability/agent-core")
print("\nResults may take a few minutes to appear in the dashboard.")
print("Evaluators assess: Goal Success Rate, Correctness, Tool Selection Accuracy")
