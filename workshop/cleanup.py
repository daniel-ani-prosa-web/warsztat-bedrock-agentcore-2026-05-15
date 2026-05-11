"""
Cleanup: Remove all workshop resources
========================================
Deletes AgentCore resources, IAM roles, Cognito, ECR, logs, and local files.
Then run scripts/cleanup.sh to delete CloudFormation stacks.
"""

import os
import sys

STRANDS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "09-AgentCore-E2E", "strands-agents"
)
sys.path.insert(0, os.path.abspath(STRANDS_DIR))
os.chdir(STRANDS_DIR)

from lab_helpers.utils import (
    agentcore_memory_cleanup,
    runtime_resource_cleanup,
    gateway_target_cleanup,
    delete_agentcore_runtime_execution_role,
    delete_customer_support_secret,
    cleanup_cognito_resources,
    delete_observability_resources,
    local_file_cleanup,
    get_ssm_parameter,
    policy_engine_cleanup,
)

print("=" * 60)
print("CLEANUP: Removing all workshop resources")
print("=" * 60)

# 1. AgentCore Memory
print("\n--- 1. Deleting AgentCore Memory ---")
try:
    memory_id = get_ssm_parameter("/app/customersupport/agentcore/memory_id")
    agentcore_memory_cleanup(memory_id)
except Exception as e:
    print(f"  Skipped: {e}")

# 1b. AgentCore Evaluation config
print("\n--- 1b. Deleting Evaluation config ---")
try:
    from bedrock_agentcore_starter_toolkit import Evaluation
    from boto3.session import Session
    eval_region = Session().region_name
    eval_client = Evaluation(region=eval_region)
    runtime_arn = get_ssm_parameter("/app/customersupport/agentcore/runtime_arn")
    agent_id = runtime_arn.split(":")[-1].split("/")[-1]
    configs = eval_client.list_online_configs(agent_id=agent_id)
    for cfg in configs.get("onlineEvaluationConfigs", []):
        cfg_id = cfg["onlineEvaluationConfigId"]
        eval_client.delete_online_config(config_id=cfg_id)
        print(f"  Deleted eval config: {cfg_id}")
except Exception as e:
    print(f"  Skipped: {e}")

# 2. AgentCore Runtime + ECR
print("\n--- 2. Deleting AgentCore Runtime + ECR ---")
try:
    runtime_arn = get_ssm_parameter("/app/customersupport/agentcore/runtime_arn")
    runtime_resource_cleanup(runtime_arn)
except Exception as e:
    print(f"  Skipped: {e}")

# 3. Policy Engine (optional)
print("\n--- 3. Deleting Policy Engine ---")
try:
    pe_id = get_ssm_parameter("/app/customersupport/agentcore/policy_engine_id")
    policy_engine_cleanup(pe_id)
except Exception as e:
    print(f"  Skipped (probably not created): {e}")

# 4. Gateway + Targets
print("\n--- 4. Deleting Gateway + Targets ---")
try:
    gateway_id = get_ssm_parameter("/app/customersupport/agentcore/gateway_id")
    gateway_target_cleanup(gateway_id)
except Exception as e:
    print(f"  Skipped: {e}")

# 5. IAM execution role
print("\n--- 5. Deleting IAM execution role ---")
try:
    delete_agentcore_runtime_execution_role()
except Exception as e:
    print(f"  Skipped: {e}")

# 6. Cognito (the one created by lab3 helpers, not CloudFormation)
print("\n--- 6. Deleting Cognito resources ---")
try:
    import json
    from lab_helpers.utils import get_customer_support_secret
    secret_str = get_customer_support_secret()
    if secret_str:
        secret = json.loads(secret_str)
        pool_id = secret.get("pool_id")
        if pool_id:
            cleanup_cognito_resources(pool_id)
    delete_customer_support_secret()
except Exception as e:
    print(f"  Skipped: {e}")

# 7. Observability resources
print("\n--- 7. Deleting observability resources ---")
try:
    delete_observability_resources()
except Exception as e:
    print(f"  Skipped: {e}")

# 8. Local files
print("\n--- 8. Cleaning local files ---")
try:
    local_file_cleanup()
except Exception as e:
    print(f"  Skipped: {e}")

print("\n" + "=" * 60)
print("CLEANUP COMPLETE (AgentCore resources)")
print("=" * 60)
print("\nNext: Delete CloudFormation stacks:")
print("  cd 09-AgentCore-E2E/strands-agents")
print("  bash scripts/cleanup.sh")
print("\nOr manually in AWS Console:")
print("  1. CloudFormation → Delete stack 'CustomerSupportStackCognito'")
print("  2. CloudFormation → Delete stack 'CustomerSupportStackInfra'")
print("  3. S3 → Empty and delete bucket 'customersupport112-{ACCOUNT_ID}-{REGION}'")
