# EdgeMind: Local SLM Intelligence Layer for Pharma Bioprocess Monitoring

---

## Problem Statement

Pharmaceutical and biotech manufacturing generates continuous high-frequency process data — pH, dissolved oxygen, temperature, agitation, feed rates — stored in historians (OSIsoft PI, AVEVA, InfluxDB) and surfaced via SCADA systems. Extracting meaning from this data requires:

- Knowledge of tag names and data structures
- Familiarity with process phases and golden batch envelopes
- Specialist data analysis skills (Python, SQL, or vendor tooling)
- Time — typically 15–30 minutes per query across multiple systems

This creates a bottleneck. Process engineers, QA reviewers, and batch record analysts spend significant time on data retrieval and comparison that could be automated — but in pharma, sending process data to a public cloud LLM endpoint is a non-starter for GxP, data sovereignty, and IP protection reasons.

**The gap:** There is no lightweight, privacy-preserving, domain-aware natural language interface for bioprocess data that runs entirely on-premise or on-device.

---

## Project Vision

Build a local SLM-powered query layer that sits between a bioprocess historian and a human operator, enabling natural language questions against real process data — with no data leaving the facility.

> *"Was pH out of spec during the exponential growth phase of batch 47?"*  
> *"Compare dissolved oxygen trajectories for the last five batches."*  
> *"Flag any temperature deviations in the last 72 hours across all active bioreactors."*

All inference runs locally. All knowledge is version-controlled. All outputs are auditable.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   OPERATOR INTERFACE                 │
│           Natural language query (CLI or web)        │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                  LOCAL SLM LAYER                     │
│   Quantised model (Gemma 3 4B / Phi-4-mini / Qwen)  │
│   Runs via Ollama on local hardware                  │
│   Grounded by markdown knowledge files at runtime    │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
┌──────────▼──────────┐   ┌──────────▼───────────────┐
│   KNOWLEDGE LAYER   │   │      MCP TOOL LAYER       │
│  golden_batch.md    │   │  classify_phase()         │
│  phase_envelopes.md │   │  get_batch_summary()      │
│  deviation_limits.md│   │  check_deviation()        │
│  process_context.md │   │  get_phase_envelope()     │
│  (version-controlled│   │  get_pca_status()         │
│   via Git)          │   │  get_correlations()       │
└─────────────────────┘   └──────────┬────────────────┘
                                     │
                          ┌──────────▼────────────────┐
                          │      DATA LAYER            │
                          │  IndPenSim V3 (prototype)  │
                          │  PI Historian (production) │
                          │  InfluxDB / CSV            │
                          └───────────────────────────┘
```

---

## Key Design Decisions

### 1. Markdown as the knowledge layer
Process knowledge — golden batch specs, phase envelopes, regulatory limits, equipment context — lives in plain markdown files checked into Git. This is:
- Auditable (version history = change control)
- Updateable without retraining the model
- Readable by both humans and SLMs
- Compatible with GxP documentation practices

### 2. MCP as the tool interface
The SLM does not query the historian directly. It calls structured MCP tools that handle data retrieval, returning typed, validated results. This separates concerns cleanly:
- SLM handles reasoning and natural language
- MCP tools handle data access and validation
- Historian remains the system of record

### 3. Local inference only
No data leaves the machine. Ollama provides the local inference runtime. Model selection prioritises quantised 4B–8B parameter models that run on CPU or modest GPU (NPU-capable edge hardware in future).

### 4. Prototype dataset: IndPenSim V3
The penicillin fermentation simulation dataset provides a realistic, freely available bioprocess time-series for development and demonstration without requiring access to real facility data.

---

## Prototype Scope (MVP)

| Component | Description | Status |
|---|---|---|
| Data layer | IndPenSim V3 CSV | Exists (HDip project) |
| MCP tools | 6 tools: classify, summarise, envelope, deviation, PCA, correlations | Exists |
| Knowledge files | golden_batch.md, phase_envelopes.md, deviation_limits.md | To build |
| Local SLM | Ollama + Gemma 3 4B or Phi-4-mini | To integrate |
| Query interface | CLI first, simple web UI second | To build |
| Evaluation | 20-query test set with expected outputs | To build |

---

## Extension Scope (Post-MVP)

- **RAG layer:** Vector store over batch records for semantic search across historical runs
- **Multi-batch reasoning:** "Which batches in Q1 had similar pH deviation patterns?"
- **Alert integration:** Push natural language summaries to Slack/Teams on deviation detection
- **PI Historian connector:** Replace IndPenSim with live OPC UA / PI Web API data source
- **Voice interface:** On-device speech-to-text for hands-free floor queries
- **Audit trail:** Log all queries and model responses with timestamps for GxP review

---

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Local inference | Ollama | Zero-cost, cross-platform, supports quantised models |
| Model | Gemma 3 4B / Phi-4-mini / Qwen2.5-3B | Runs on CPU, small enough for edge hardware |
| MCP framework | FastMCP (Python) | Already in use in prototype |
| Knowledge files | Markdown + Git | Auditable, human-readable, version-controlled |
| Data layer | Pandas + CSV | Lightweight, works offline |
| Query interface | Click (CLI) → Flask (web) | Minimal, familiar stack |
| Prototype data | IndPenSim V3 | Open, realistic bioprocess simulation |

---

## Why This Matters

**For pharma manufacturing:**  
Reduces analyst dependency for routine batch interrogation. Accelerates deviation investigation. Enables floor-level staff to ask process questions without specialist tooling.

**For GxP compliance:**  
All inference is local. Knowledge is version-controlled. No proprietary process data touches a public endpoint. Audit trail is append-only.

**For the edge AI trajectory:**  
Demonstrates the SLM + MCP + markdown knowledge pattern that is emerging as the practical architecture for industrial edge intelligence — before vendors package and price it.

---

## Repository Structure

```
Bioprocess_Monitoring_Edge_Mind/
├── README.md
├── CLAUDE.md                  # Project context for AI-assisted dev
├── knowledge/
│   ├── golden_batch.md
│   ├── phase_envelopes.md
│   └── deviation_limits.md
├── mcp_server/
│   ├── server.py              # FastMCP server
│   └── tools/
├── data/
│   └── indpensim_v3/
├── slm_layer/
│   ├── query.py               # Ollama integration
│   └── prompts/
├── interface/
│   └── cli.py
├── eval/
│   └── test_queries.json
└── docs/
    └── architecture.md
```

---