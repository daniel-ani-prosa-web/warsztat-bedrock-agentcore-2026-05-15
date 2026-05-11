"""
Lab 1: Customer Support Agent Prototype
========================================
Builds a Strands agent with 4 tools: return policy, product info, web search, technical support (KB).
Run: python lab1.py
"""

import os
import sys
import time

import boto3
from boto3.session import Session
from ddgs import DDGS
from ddgs.exceptions import DDGSException, RatelimitException
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool
from strands_tools import retrieve

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL_ID = "global.amazon.nova-2-lite-v1:0"

boto_session = Session()
region = boto_session.region_name
account_id = boto3.client("sts").get_caller_identity()["Account"]

print(f"Account: {account_id}  Region: {region}")

# ---------------------------------------------------------------------------
# Step 1: Sync Knowledge Base
# ---------------------------------------------------------------------------
print("\n--- Step 1: Syncing Bedrock Knowledge Base ---")

ssm = boto3.client("ssm")
bedrock_agent = boto3.client("bedrock-agent")
s3 = boto3.client("s3")

kb_id = ssm.get_parameter(Name=f"/{account_id}-{region}/kb/knowledge-base-id")["Parameter"]["Value"]
ds_id = ssm.get_parameter(Name=f"/{account_id}-{region}/kb/data-source-id")["Parameter"]["Value"]

print(f"Knowledge Base ID: {kb_id}")
print(f"Data Source ID:    {ds_id}")

response = bedrock_agent.start_ingestion_job(
    knowledgeBaseId=kb_id, dataSourceId=ds_id, description="Workshop sync"
)
job_id = response["ingestionJob"]["ingestionJobId"]
print(f"Ingestion job started: {job_id}")

while True:
    job = bedrock_agent.get_ingestion_job(
        knowledgeBaseId=kb_id, dataSourceId=ds_id, ingestionJobId=job_id
    )["ingestionJob"]
    status = job["status"]
    print(f"  Status: {status}")
    if status in ("COMPLETE", "FAILED"):
        break
    time.sleep(5)

if status != "COMPLETE":
    print(f"KB sync failed: {status}")
    sys.exit(1)

file_count = job.get("statistics", {}).get("numberOfDocumentsScanned", 0)
print(f"KB sync complete — {file_count} documents ingested")

# ---------------------------------------------------------------------------
# Step 2: Define tools
# ---------------------------------------------------------------------------
print("\n--- Step 2: Defining agent tools ---")


@tool
def get_return_policy(product_category: str) -> str:
    """Get return policy information for a specific product category.

    Args:
        product_category: Electronics category (e.g., 'smartphones', 'laptops', 'accessories')
    Returns:
        Formatted return policy details including timeframes and conditions
    """
    return_policies = {
        "smartphones": {
            "window": "30 days",
            "condition": "Original packaging, no physical damage, factory reset required",
            "process": "Online RMA portal or technical support",
            "refund_time": "5-7 business days after inspection",
            "shipping": "Free return shipping, prepaid label provided",
            "warranty": "1-year manufacturer warranty included",
        },
        "laptops": {
            "window": "30 days",
            "condition": "Original packaging, all accessories, no software modifications",
            "process": "Technical support verification required before return",
            "refund_time": "7-10 business days after inspection",
            "shipping": "Free return shipping with original packaging",
            "warranty": "1-year manufacturer warranty, extended options available",
        },
        "accessories": {
            "window": "30 days",
            "condition": "Unopened packaging preferred, all components included",
            "process": "Online return portal",
            "refund_time": "3-5 business days after receipt",
            "shipping": "Customer pays return shipping under $50",
            "warranty": "90-day manufacturer warranty",
        },
    }
    default_policy = {
        "window": "30 days",
        "condition": "Original condition with all included components",
        "process": "Contact technical support",
        "refund_time": "5-7 business days after inspection",
        "shipping": "Return shipping policies vary",
        "warranty": "Standard manufacturer warranty applies",
    }
    policy = return_policies.get(product_category.lower(), default_policy)
    return (
        f"Return Policy - {product_category.title()}:\n\n"
        f"  Return window: {policy['window']} from delivery\n"
        f"  Condition: {policy['condition']}\n"
        f"  Process: {policy['process']}\n"
        f"  Refund timeline: {policy['refund_time']}\n"
        f"  Shipping: {policy['shipping']}\n"
        f"  Warranty: {policy['warranty']}"
    )


@tool
def get_product_info(product_type: str) -> str:
    """Get detailed technical specifications and information for electronics products.

    Args:
        product_type: Electronics product type (e.g., 'laptops', 'smartphones', 'headphones', 'monitors')
    Returns:
        Formatted product information including warranty, features, and policies
    """
    products = {
        "laptops": {
            "warranty": "1-year manufacturer warranty + optional extended coverage",
            "specs": "Intel/AMD processors, 8-32GB RAM, SSD storage, various display sizes",
            "features": "Backlit keyboards, USB-C/Thunderbolt, Wi-Fi 6, Bluetooth 5.0",
            "compatibility": "Windows 11, macOS, Linux support varies by model",
            "support": "Technical support and driver updates included",
        },
        "smartphones": {
            "warranty": "1-year manufacturer warranty",
            "specs": "5G/4G connectivity, 128GB-1TB storage, multiple camera systems",
            "features": "Wireless charging, water resistance, biometric security",
            "compatibility": "iOS/Android, carrier unlocked options available",
            "support": "Software updates and technical support included",
        },
        "headphones": {
            "warranty": "1-year manufacturer warranty",
            "specs": "Wired/wireless options, noise cancellation, 20Hz-20kHz frequency",
            "features": "Active noise cancellation, touch controls, voice assistant",
            "compatibility": "Bluetooth 5.0+, 3.5mm jack, USB-C charging",
            "support": "Firmware updates via companion app",
        },
        "monitors": {
            "warranty": "3-year manufacturer warranty",
            "specs": "4K/1440p/1080p resolutions, IPS/OLED panels, various sizes",
            "features": "HDR support, high refresh rates, adjustable stands",
            "compatibility": "HDMI, DisplayPort, USB-C inputs",
            "support": "Color calibration and technical support",
        },
    }
    product = products.get(product_type.lower())
    if not product:
        return f"Technical specifications for {product_type} not available."
    return (
        f"Technical Information - {product_type.title()}:\n\n"
        f"  Warranty: {product['warranty']}\n"
        f"  Specifications: {product['specs']}\n"
        f"  Key Features: {product['features']}\n"
        f"  Compatibility: {product['compatibility']}\n"
        f"  Support: {product['support']}"
    )


@tool
def web_search(keywords: str, region: str = "us-en", max_results: int = 5) -> str:
    """Search the web for updated information.

    Args:
        keywords: The search query keywords.
        region: The search region (wt-wt, us-en, uk-en, etc.)
        max_results: The maximum number of results to return.
    Returns:
        List of search results.
    """
    try:
        results = DDGS().text(keywords, region=region, max_results=max_results)
        return results if results else "No results found."
    except RatelimitException:
        return "Rate limit reached. Please try again later."
    except DDGSException as e:
        return f"Search error: {e}"
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def get_technical_support(issue_description: str) -> str:
    """Search the knowledge base for technical support documentation.

    Args:
        issue_description: Description of the technical issue to look up.
    Returns:
        Relevant technical support information.
    """
    try:
        _ssm = boto3.client("ssm")
        _account_id = boto3.client("sts").get_caller_identity()["Account"]
        _region = boto3.Session().region_name

        _kb_id = _ssm.get_parameter(Name=f"/{_account_id}-{_region}/kb/knowledge-base-id")[
            "Parameter"
        ]["Value"]

        tool_use = {
            "toolUseId": "tech_support_query",
            "input": {
                "text": issue_description,
                "knowledgeBaseId": _kb_id,
                "region": _region,
                "numberOfResults": 3,
                "score": 0.4,
            },
        }
        result = retrieve.retrieve(tool_use)
        if result["status"] == "success":
            return result["content"][0]["text"]
        return f"Unable to access technical support documentation. Error: {result['content'][0]['text']}"
    except Exception as e:
        return f"Unable to access technical support documentation. Error: {str(e)}"


print("All 4 tools ready: get_return_policy, get_product_info, web_search, get_technical_support")

# ---------------------------------------------------------------------------
# Step 3: Create the agent
# ---------------------------------------------------------------------------
print("\n--- Step 3: Creating Customer Support Agent ---")

SYSTEM_PROMPT = """You are a helpful and professional customer support assistant for an electronics e-commerce company.
Your role is to:
- Provide accurate information using the tools available to you
- Support the customer with technical information and product specifications, and maintenance questions
- Be friendly, patient, and understanding with customers
- Always offer additional help after answering questions
- If you can't help with something, direct customers to the appropriate contact

You have access to the following tools:
1. get_return_policy() - For warranty and return policy questions
2. get_product_info() - To get information about a specific product
3. web_search() - To access current technical documentation, or for updated information.
4. get_technical_support() - For troubleshooting issues, setup guides, maintenance tips, and detailed technical assistance
For any technical problems, setup questions, or maintenance concerns, always use the get_technical_support() tool as it contains our comprehensive technical documentation and step-by-step guides.

Always use the appropriate tool to get accurate, up-to-date information rather than making assumptions about electronic products or specifications."""

model = BedrockModel(
    model_id=MODEL_ID,
    temperature=0.3,
    region_name=region,
)

agent = Agent(
    model=model,
    tools=[get_product_info, get_return_policy, web_search, get_technical_support],
    system_prompt=SYSTEM_PROMPT,
)

print("Agent created successfully!")

# ---------------------------------------------------------------------------
# Step 4: Test the agent
# ---------------------------------------------------------------------------
print("\n--- Step 4: Testing the agent ---")

test_queries = [
    "What's the return policy for my ThinkPad X1 Carbon?",
    "My laptop won't turn on, what should I check?",
    "I bought an iPhone 14 last month. It heats up. How do I solve it?",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}: {query}")
    print("=" * 60)
    response = agent(query)
    print()

print("\n--- Lab 1 Complete ---")
print("Resources used: Bedrock KB (read-only), Bedrock model (Nova 2 Lite)")
print("No new AWS resources were created in this lab.")
