# cost-cutting-agent

A FinOps agent that flags cloud cost anomalies and explains them using
[Hindsight](https://github.com/vectorize-io/hindsight) memory, so it stops
repeating suggestions a team already rejected.

## Why

Cost anomaly detection is easy. The hard part is the second conversation:
"we told you last month we can't turn off that VM, remember?" Most agents
don't remember. This one does, via Hindsight's `retain` / `recall` / `reflect`
operations and its observation layer (facts that get refined with evidence
over time instead of overwritten).

## Architecture

```
billing CSV --> detector.py (pandas z-score) --> anomalies
                                                      |
                                                      v
                                          memory.py (Hindsight client)
                                          - recall: past decisions for this service/team
                                          - retain: new anomaly + outcome
                                          - reflect: team-level cost pattern summary
                                                      |
                                                      v
                                              LLM (advice, informed by memory)
```

## Setup

1. Start a Hindsight server (see the [Hindsight quick start](https://github.com/vectorize-io/hindsight#quick-start)):

```bash
export OPENAI_API_KEY=sk-xxx
docker run -it --pull always --name hindsight -p 8888:8888 -p 9999:9999 \
  -e HINDSIGHT_API_LLM_API_KEY=$OPENAI_API_KEY \
  -v hindsight-data:/home/hindsight/.pg0 \
  ghcr.io/vectorize-io/hindsight:latest
```

2. Install this project:

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY
```

3. Generate synthetic billing data:

```bash
python data/generate_synthetic_billing.py
```

4. Run the API:

```bash
uvicorn app.main:app --reload
```

5. Try it:

```bash
curl -X POST "http://localhost:8000/analyze?billing_csv_path=data/billing.csv&team=data-science"
```

## Endpoints

| Endpoint | What it does |
|---|---|
| `POST /analyze` | Detects anomalies in a billing CSV, recalls memory per anomaly, returns LLM advice |
| `POST /decision` | Records whether a suggestion was accepted or rejected (this is what makes memory useful) |
| `GET /briefing/{team}` | Reflects on a team's full cost history and returns a summary |

## Known limitations

- Anomaly detection is a simple z-score, not seasonality-aware. Real billing
  has weekly/monthly cycles this will false-positive on.
- Memory is only as good as what gets retained — if `/decision` is never
  called, the agent never learns which suggestions were rejected.
- No auth/multi-tenant isolation beyond Hindsight's per-bank isolation
  (one bank per team here).
