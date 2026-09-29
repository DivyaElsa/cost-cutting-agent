import os

import pandas as pd
from fastapi import FastAPI
from openai import OpenAI

from app.detector import detect_anomalies
from app.memory import CostMemory

app = FastAPI(title="Cost-Cutting Cloud Agent")
memory = CostMemory(base_url=os.getenv("HINDSIGHT_API_URL", "http://localhost:8888"))
llm = OpenAI()

SYSTEM_PROMPT = (
    "You are a FinOps analyst. Use the team's memory to avoid repeating "
    "suggestions that were already rejected. Be specific and cite what "
    "happened last time if it's relevant."
)


@app.post("/analyze")
def analyze(billing_csv_path: str, team: str):
    df = pd.read_csv(billing_csv_path)
    anomalies = detect_anomalies(df)

    results = []
    for _, row in anomalies.iterrows():
        context = memory.recall_context(team, row.service)

        prompt = (
            f"Anomaly: {row.service} cost ${row.cost:.2f} (z-score {row.z:.2f}).\n"
            f"Relevant memory: {context}"
        )
        advice = (
            llm.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            .choices[0]
            .message.content
        )

        memory.retain_anomaly(team, row.service, row.cost, row.z)
        results.append(
            {
                "service": row.service,
                "cost": row.cost,
                "z_score": row.z,
                "advice": advice,
                "memory_used": context,
            }
        )

    return results


@app.post("/decision")
def decision(team: str, service: str, suggestion: str, accepted: bool, saving: float = 0.0):
    memory.retain_decision(team, service, suggestion, accepted, saving)
    return {"status": "recorded"}


@app.get("/briefing/{team}")
def briefing(team: str):
    summary = memory.reflect_on_team(team)
    return {"team": team, "summary": summary}
