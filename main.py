import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'slm_layer'))

from edge_mind import ask_ollama, call_tool


async def run():
    print("EdgeMind — Bioprocess Monitoring Intelligence Layer")
    print("=" * 50)
    print("Type 'exit', 'quit', 'stop', or 'q' to stop.\n")

    while True:
        question = input("Ask a bioprocess question: ").strip()

        if question.lower() in ("exit", "quit", "stop", "q", ""):
            print("Shutting down EdgeMind.")
            break

        print("\nThinking...")

        try:
            tool_call = ask_ollama(question)
            print(f"Tool selected: {tool_call}")

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
            print(f"\nResult:\n{result}\n")
            print("-" * 50)

        except Exception as e:
            print(f"Error: {e}\n")
            print("-" * 50)


if __name__ == "__main__":
    asyncio.run(run())