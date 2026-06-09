# EdgeMind — Local SLM Intelligence Layer for Bioprocess Monitoring

A local, privacy-preserving natural language interface for pharma bioprocess data. Ask questions in plain English against real fermentation data — no data leaves the machine.

---

## What It Does

```
"tell me about batch 4 at time 30"
        ↓
  phi3:mini (local, Ollama)
        ↓
  selects MCP tool + parameters
        ↓
  pharma-analytics MCP server (IndPenSim V3 data)
        ↓
  structured result returned to operator
```

No cloud. No API keys. No process data leaving the facility.

---

## Architecture

```
Operator (CLI)
      ↓
EdgeMind SLM Layer (slm_layer/edge_mind.py)
  - Ollama / phi3:mini
  - Grounded by knowledge/golden_batch.md
      ↓
MCP Tool Layer (mcp_server/server.py)
  - FastMCP server
  - 7 pharma analytics tools
      ↓
Data Layer
  - IndPenSim V3 penicillin fermentation dataset
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com/download) installed and running
- phi3:mini pulled: `ollama pull phi3:mini`

### Setup

```bash
git clone https://github.com/skerr17/Bioprocess_Monitoring_Edge_Mind
cd Bioprocess_Monitoring_Edge_Mind
uv sync
```

### Run the MCP server (terminal 1)

```bash
cd mcp_server
uv run python server.py
```

### Run EdgeMind (terminal 2)

```bash
python main.py
```

---

## Example Queries

```
Ask a bioprocess question: tell me about batch 4
Ask a bioprocess question: is batch 9 showing a deviation?
Ask a bioprocess question: what was batch 9 like at time 150?
Ask a bioprocess question: what phase is batch 3 at hour 50?
```

Type `exit`, `quit`, `stop`, or `q` to close.

---

## Available Tools

| Tool | Description |
|---|---|
| `get_batch_summary(batch_id)` | Descriptive stats for a batch |
| `check_deviation(batch_id, time_h)` | Hotelling T² status at a given hour |
| `classify_phase(batch_id, time_h)` | Fermentation phase at a given hour |
| `get_correlations()` | Correlation matrix for process variables |
| `get_pca_status(batch_id, time_h)` | PCA scores at a time point |
| `get_phase_envelope(phase)` | Operating envelope for a phase |
| `get_latest_time(batch_id)` | Most recent recorded time point |

If no time is given for time-dependent tools, EdgeMind automatically fetches the latest recorded time for that batch.

---

## Knowledge Layer

Process knowledge lives in `knowledge/golden_batch.md` — plain markdown checked into Git. This includes:
- Normal operating ranges per variable
- Deviation alert thresholds
- Fermentation phase definitions and hour ranges

Updating a limit means editing one line in the markdown file. No retraining required.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Local inference | Ollama |
| Model | phi3:mini (CPU, ~2.3GB) |
| MCP framework | FastMCP 3.4.2 |
| Knowledge files | Markdown + Git |
| Data | IndPenSim V3 (penicillin fermentation simulation) |
| Entry point | Python CLI with asyncio loop |

---

## Project Status

**MVP complete.** Core pipeline working end to end:
- [x] Natural language → tool routing via local SLM
- [x] Auto time resolution (fetches latest recording if no time given)
- [x] Domain knowledge grounding via markdown
- [x] Clean CLI loop with graceful exit
- [x] Error handling for malformed model responses

**Planned extensions:**
- [ ] Plain English summaries of raw JSON results
- [ ] Multi-turn conversation context
- [ ] Batch comparison tool
- [ ] Evaluation set (20 test queries with expected outputs)
- [ ] Flask web interface

---

## Why Local?

In GxP pharmaceutical manufacturing, sending process data to a public cloud LLM endpoint is a non-starter — data sovereignty, IP protection, and regulatory audit requirements all point toward on-premise inference. EdgeMind demonstrates the SLM + MCP + markdown knowledge pattern as a practical architecture for industrial edge intelligence.

---

## Dataset

[IndPenSim V3](http://www.industrialpenicillinsimulation.com/) — open penicillin fermentation simulation dataset. Used here as a realistic bioprocess prototype without requiring access to real facility data.