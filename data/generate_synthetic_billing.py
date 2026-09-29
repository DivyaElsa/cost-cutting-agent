import random
from datetime import datetime, timedelta

import pandas as pd

SERVICES = ["compute-vm", "blob-storage", "data-egress", "gpu-cluster", "managed-db"]
TEAMS = ["data-science", "platform", "growth"]


def generate(days: int = 90, out_path: str = "data/billing.csv") -> pd.DataFrame:
    rows = []
    start = datetime.today() - timedelta(days=days)
    base_cost = {s: random.uniform(50, 400) for s in SERVICES}

    for d in range(days):
        date = start + timedelta(days=d)
        for team in TEAMS:
            for service in SERVICES:
                cost = base_cost[service] * random.uniform(0.85, 1.15)

                # Recurring anomaly: a GPU cluster left running over a
                # weekend, roughly once a month.
                if service == "gpu-cluster" and team == "data-science" and d % 30 == 12:
                    cost *= 4.5

                # One-off anomaly: a backup misconfiguration spikes egress.
                if service == "data-egress" and d == 45:
                    cost *= 3.2

                rows.append(
                    {
                        "date": date.date().isoformat(),
                        "team": team,
                        "service": service,
                        "cost": round(cost, 2),
                    }
                )

    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
    return df


if __name__ == "__main__":
    generate()
