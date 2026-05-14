"""
Lab 7: AgentCore Harness — Agent in One API Call
==================================================
Standalone lab. No dependency on Labs 1-6.
Creates a Harness agent, invokes it, runs commands on its VM, cleans up.
"""

import sys
import os
import time
import uuid
import json

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "11-AgentCore-harness",
    ),
)

import boto3
from helper.iam import create_harness_role, delete_harness_role
from helper.client import get_agentcore_control_client, get_agentcore_client

account_id = boto3.client("sts").get_caller_identity()["Account"]
region = boto3.session.Session().region_name
print(f"Account: {account_id}, Region: {region}")

# ---------------------------------------------------------------------------
# Step 1: Create IAM execution role
# ---------------------------------------------------------------------------
print("\n--- Step 1: Creating IAM execution role ---")
role_arn = create_harness_role()
print(f"Role ARN: {role_arn}")
print("Waiting 10s for IAM propagation...")
time.sleep(10)

# ---------------------------------------------------------------------------
# Step 2: Create Harness agent
# ---------------------------------------------------------------------------
print("\n--- Step 2: Creating Harness agent ---")

control = get_agentcore_control_client()
client = get_agentcore_client()

HARNESS_NAME = f"Workshop_{uuid.uuid4().hex[:8]}"

resp = control.create_harness(
    harnessName=HARNESS_NAME,
    executionRoleArn=role_arn,
)
harness = resp["harness"]
harness_id = harness["harnessId"]
harness_arn = harness["arn"]
print(f"Harness: {HARNESS_NAME}")
print(f"Harness ID: {harness_id}")
print(f"Status: {harness['status']}")

for i in range(12):
    resp = control.get_harness(harnessId=harness_id)
    status = resp["harness"]["status"]
    print(f"  Attempt {i+1}: {status}")
    if status == "READY":
        print("Harness is READY")
        break
    time.sleep(5)
else:
    print("ERROR: Harness did not become READY in 60s")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 3: Invoke agent — ask a question, agent saves to file
# ---------------------------------------------------------------------------
MODEL_ID = os.environ.get("BEDROCK_HARNESS_MODEL_ID", "amazon.nova-lite-v1:0")
print(f"\n--- Step 3: Invoking agent ({MODEL_ID}) ---")

session_id = str(uuid.uuid4()).upper()
print(f"Session ID: {session_id}\n")

response = client.invoke_harness(
    harnessArn=harness_arn,
    runtimeSessionId=session_id,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": "What are three fun things to do in Seattle on a rainy day? "
                    "Save your answer to a Markdown file called seattle.md"
                }
            ],
        }
    ],
    model={
        "bedrockModelConfig": {
            "modelId": MODEL_ID
        }
    },
)

for event in response["stream"]:
    if "contentBlockStart" in event:
        start = event["contentBlockStart"].get("start", {})
        if "toolUse" in start:
            print(f"\n[Tool: {start['toolUse'].get('name', '?')}]", flush=True)
    elif "contentBlockDelta" in event:
        delta = event["contentBlockDelta"].get("delta", {})
        if "text" in delta:
            print(delta["text"], end="", flush=True)
    elif "messageStop" in event:
        print()
    elif "internalServerException" in event:
        print(f"\nError: {event['internalServerException']}")

# ---------------------------------------------------------------------------
# Step 4: Execute commands on agent's microVM
# ---------------------------------------------------------------------------
print("\n--- Step 4: Running commands on agent's microVM ---")


def run_on_vm(cmd: str):
    print(f"\n$ {cmd}")
    resp = client.invoke_agent_runtime_command(
        agentRuntimeArn=harness_arn,
        runtimeSessionId=session_id,
        body={"command": cmd},
    )
    for event in resp["stream"]:
        if "chunk" in event:
            chunk = event["chunk"]
            if "contentDelta" in chunk:
                d = chunk["contentDelta"]
                if "stdout" in d:
                    print(d["stdout"], end="", flush=True)
                if "stderr" in d:
                    print(d["stderr"], end="", flush=True)
            elif "contentStop" in chunk:
                print(f"\n[exit: {chunk['contentStop']['exitCode']}]")


run_on_vm("pwd")
run_on_vm("ls -la")
run_on_vm("cat seattle.md")

# ---------------------------------------------------------------------------
# Step 5: Cleanup
# ---------------------------------------------------------------------------
print("\n--- Step 5: Cleanup ---")
control.delete_harness(harnessId=harness_id)
print(f"Deleted harness: {harness_id}")

delete_harness_role()

print("\n--- Lab 7 Complete ---")
print("Harness = agent w jednym API call, zero frameworkow, zero Dockera.")
print("Kazda sesja biegnie w izolowanym Firecracker microVM.")
