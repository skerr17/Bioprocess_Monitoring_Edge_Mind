import requests
import json
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp_server'))

from server import (
    get_batch_summary,
    check_deviation,
    classify_phase,
    get_correlations,
    get_pca_status,
    get_phase_envelope,
    get_latest_time,
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"

TOOL_DESCRIPTIONS = """
You are an assistant for bioprocess monitoring. You have access to these tools:

1. get_batch_summary(batch_id) - Get descriptive stats for a batch (e.g. batch_id=1)
2. check_deviation(batch_id, time_h) - Check if a batch is deviating at a given hour. If no time given, first call get_latest_time to find the latest recording.
3. classify_phase(batch_id, time_h) - Classify fermentation phase at a given hour. If no time given, first call get_latest_time.
4. get_correlations() - Get correlation matrix for process variables
5. get_pca_status(batch_id, time_h) - Get PCA scores for a batch at a time point. If no time given, first call get_latest_time.
6. get_phase_envelope(phase) - Get operating envelope for a phase (e.g. phase="exponential")
7. get_latest_time(batch_id) - Get the most recent time point recorded for a batch

Given a user question, respond ONLY with a JSON object like this:
{"tool": "get_batch_summary", "params": {"batch_id": 1}}

If you need to call get_latest_time first, return that call first.
No explanation. JSON only.
"""

TOOL_MAP = {
    "get_batch_summary": get_batch_summary,
    "check_deviation": check_deviation,
    "classify_phase": classify_phase,
    "get_correlations": get_correlations,
    "get_pca_status": get_pca_status,
    "get_phase_envelope": get_phase_envelope,
    "get_latest_time": get_latest_time,
}

def load_knowledge() -> str:
    knowledge_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'golden_batch.md')
    with open(knowledge_path, 'r') as f:
        return f.read()


def ask_ollama(question: str, extra_context: str = "") -> dict:
    knowledge = load_knowledge()

    prompt = TOOL_DESCRIPTIONS + f"""
## Domain Knowledge
{knowledge}
{extra_context}
User question: {question}
"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })

    result = response.json()
    raw = result["response"].strip()

    start = raw.find("{")
    depth = 0
    end = start
    for i, ch in enumerate(raw[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    json_str = raw[start:end]
    return json.loads(json_str)


async def call_tool(tool_call: dict) -> str:
    tool_name = tool_call["tool"]
    params = tool_call.get("params", {})

    if tool_name not in TOOL_MAP:
        return f"Unknown tool: {tool_name}"

    fn = TOOL_MAP[tool_name]
    result = await fn(**params)
    return result


async def main():
    question = input("Ask a bioprocess question: ")
    print("\nThinking...")

    tool_call = ask_ollama(question)
    print(f"Tool selected: {tool_call}")

    # If model chose get_latest_time, use result to make a second call
    if tool_call["tool"] == "get_latest_time":
        latest_result = await call_tool(tool_call)
        print(f"Latest time fetched: {latest_result}")
        latest_data = json.loads(latest_result)
        latest_time = latest_data["latest_time_h"]
        batch_id = tool_call["params"]["batch_id"]
        extra_context = f"\n## Latest time for batch {batch_id} is {latest_time}h. Now answer the original question using this time.\n"
        tool_call = ask_ollama(question, extra_context)
        print(f"Second tool selected: {tool_call}")

    # Defensively fill in missing time_h for tools that require it
    time_required_tools = ["check_deviation", "classify_phase", "get_pca_status"]
    if tool_call["tool"] in time_required_tools and not tool_call.get("params", {}).get("time_h"):        
        batch_id = tool_call["params"]["batch_id"]
        print(f"No time given — fetching latest time for batch {batch_id}...")
        latest_result = await call_tool({"tool": "get_latest_time", "params": {"batch_id": batch_id}})
        latest_data = json.loads(latest_result)
        tool_call["params"]["time_h"] = latest_data["latest_time_h"]
        print(f"Using time_h={tool_call['params']['time_h']}")

    print("\nFetching data...")
    result = await call_tool(tool_call)
    print(f"\nResult:\n{result}")
    


if __name__ == "__main__":
    asyncio.run(main())