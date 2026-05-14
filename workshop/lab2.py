"""
Lab 2: Enhance Agent with AgentCore Memory
============================================
Adds persistent short-term and long-term memory to the customer support agent.
Run from strands-agents/ directory: python ../../workshop/lab2.py
"""

import logging
import os
import sys
import time
import uuid

STRANDS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "09-AgentCore-E2E", "strands-agents"
)
sys.path.insert(0, os.path.abspath(STRANDS_DIR))

import boto3
from boto3.session import Session
from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType
from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig,
    RetrievalConfig,
)
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)
from strands import Agent
from strands.models import BedrockModel

from lab_helpers.lab1_strands_agent import (
    SYSTEM_PROMPT,
    MODEL_ID,
    get_return_policy,
    get_product_info,
    web_search,
    get_technical_support,
)
from lab_helpers.utils import put_ssm_parameter

logging.basicConfig(level=logging.WARNING)

boto_session = Session()
REGION = boto_session.region_name
ACTOR_ID = "customer_001"

print(f"Region: {REGION}")

# ---------------------------------------------------------------------------
# Step 1: Create AgentCore Memory
# ---------------------------------------------------------------------------
print("\n--- Step 1: Creating AgentCore Memory ---")
print("This provisions vector DBs + processing pipelines. Takes 2-3 minutes on first run.")

memory_name = "CustomerSupportMemory"
memory_manager = MemoryManager(region_name=REGION)

memory = memory_manager.get_or_create_memory(
    name=memory_name,
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
if not memory_id:
    print("ERROR: Memory resource not created.")
    sys.exit(1)

put_ssm_parameter("/app/customersupport/agentcore/memory_id", memory_id)
print(f"Memory ID: {memory_id}")

# ---------------------------------------------------------------------------
# Step 2: Seed previous customer interactions
# ---------------------------------------------------------------------------
print("\n--- Step 2: Seeding customer history ---")

previous_interactions = [
    ("I'm having issues with my MacBook Pro overheating during video editing.", "USER"),
    (
        "I can help with that thermal issue. For video editing workloads, let's check your Activity Monitor "
        "and adjust performance settings. Your MacBook Pro order #MB-78432 is still under warranty.",
        "ASSISTANT",
    ),
    (
        "What's the return policy on gaming headphones? I need low latency for competitive FPS games",
        "USER",
    ),
    (
        "For gaming headphones, you have 30 days to return. Since you're into competitive FPS, "
        "I'd recommend checking the audio latency specs - most gaming models have <40ms latency.",
        "ASSISTANT",
    ),
    (
        "I need a laptop under $1200 for programming. Prefer 16GB RAM minimum and good Linux compatibility. "
        "I like ThinkPad models.",
        "USER",
    ),
    (
        "Perfect! For development work, I'd suggest looking at our ThinkPad E series or Dell XPS models. "
        "Both have excellent Linux support and 16GB RAM options within your budget.",
        "ASSISTANT",
    ),
]

memory_client = MemoryClient(region_name=REGION)
memory_client.create_event(
    memory_id=memory_id,
    actor_id=ACTOR_ID,
    session_id="previous_session",
    messages=previous_interactions,
)
print("Interactions saved to Short-Term Memory")
print("Long-Term Memory processing will begin automatically...")

# ---------------------------------------------------------------------------
# Step 3: Wait for LTM processing
# ---------------------------------------------------------------------------
print("\n--- Step 3: Waiting for Long-Term Memory extraction ---")

max_retries = 12
for attempt in range(max_retries):
    memories = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace=f"support/customer/{ACTOR_ID}/preferences/",
        query="can you summarize the support issue",
    )
    if memories:
        print(f"Found {len(memories)} preference memories after {attempt * 10}s")
        break
    print(f"  Still processing... ({attempt + 1}/{max_retries})")
    time.sleep(10)
else:
    print("WARNING: LTM processing taking longer than expected. Continuing anyway.")

if memories:
    print("\nExtracted customer preferences:")
    for i, mem in enumerate(memories, 1):
        if isinstance(mem, dict):
            text = mem.get("content", {}).get("text", "")
            if text:
                print(f"  {i}. {text}")

# Check semantic memories too
print("\nChecking semantic memories...")
for attempt in range(6):
    semantic = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace=f"support/customer/{ACTOR_ID}/semantic/",
        query="information on the technical support issue",
    )
    if semantic:
        print(f"Found {len(semantic)} semantic memories")
        for i, mem in enumerate(semantic, 1):
            if isinstance(mem, dict):
                text = mem.get("content", {}).get("text", "")
                if text:
                    print(f"  {i}. {text}")
        break
    time.sleep(10)

# ---------------------------------------------------------------------------
# Step 4: Create memory-enhanced agent
# ---------------------------------------------------------------------------
print("\n--- Step 4: Creating memory-enhanced agent ---")

session_id = str(uuid.uuid4())

memory_config = AgentCoreMemoryConfig(
    memory_id=memory_id,
    session_id=session_id,
    actor_id=ACTOR_ID,
    retrieval_config={
        "support/customer/{actorId}/semantic/": RetrievalConfig(top_k=3, relevance_score=0.2),
        "support/customer/{actorId}/preferences/": RetrievalConfig(top_k=3, relevance_score=0.2),
    },
)

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)

agent = Agent(
    model=model,
    session_manager=AgentCoreMemorySessionManager(memory_config, REGION),
    tools=[get_product_info, get_return_policy, web_search, get_technical_support],
    system_prompt=SYSTEM_PROMPT,
)

print("Memory-enhanced agent created!")

# ---------------------------------------------------------------------------
# Step 5: Test personalized responses
# ---------------------------------------------------------------------------
print("\n--- Step 5: Testing personalized responses ---")

print("\n" + "=" * 60)
print("Test 1: Which headphones would you recommend?")
print("(Agent should recall gaming/FPS preferences)")
print("=" * 60)
response1 = agent("Which headphones would you recommend?")

print("\n" + "=" * 60)
print("Test 2: What is my preferred laptop brand and requirements?")
print("(Agent should recall ThinkPad, 16GB RAM, Linux, $1200 budget)")
print("=" * 60)
response2 = agent("What is my preferred laptop brand and requirements?")

print("\n--- Lab 2 Complete ---")
print(f"Resources created: AgentCore Memory '{memory_name}' (ID: {memory_id})")
print("SSM parameter: /app/customersupport/agentcore/memory_id")
