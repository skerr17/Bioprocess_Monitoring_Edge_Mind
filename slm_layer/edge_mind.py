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
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"

TOOL_DESCRIPTIONS = """
You are an assistant for bioprocess monitoring. You have access to these tools:

1. get_batch_summary(batch_id) - Get descriptive stats for a batch (e.g. batch_id=1)
2. check_deviation(batch_id, time_point) - Check if a batch is deviating at a given hour
3. classify_phase(batch_id, time_point) - Classify fermentation phase at a given hour
4. get_correlations() - Get correlation matrix for process variables
5. get_pca_status(batch_id, time_point) - Get PCA scores for a batch at a time point
6. get_phase_envelope(phase) - Get operating envelope for a phase (e.g. phase="exponential")

Given a user question, respond ONLY with a JSON object like this:
{"tool": "get_batch_summary", "params": {"batch_id": 1}}

No explanation. JSON only.
"""

TOOL_MAP = {
    "get_batch_summary": get_batch_summary,
    "check_deviation": check_deviation,
    "classify_phase": classify_phase,
    "get_correlations": get_correlations,
    "get_pca_status": get_pca_status,
    "get_phase_envelope": get_phase_envelope,
}

def ask_ollama(question: str) -> dict:
    prompt = TOOL_DESCRIPTIONS + f"\nUser question: {question}\n"
    
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })
    
    result = response.json()
    raw = result["response"].strip()
    
    # Take only the first JSON object
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
    
    print("\nFetching data...")
    result = await call_tool(tool_call)
    print(f"\nResult:\n{result}")

if __name__ == "__main__":
    asyncio.run(main())
