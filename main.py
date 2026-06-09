import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'slm_layer'))

from edge_mind import main as edge_mind_main


if __name__ == "__main__":
    print("EdgeMind — Bioprocess Monitoring Intelligence Layer")
    print("=" * 50)
    asyncio.run(edge_mind_main())