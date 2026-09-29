import pandas as pd


def detect_anomalies(df: pd.DataFrame, z_thresh: float = 2.5) -> pd.DataFrame:
    """Flag rows whose cost deviates from that service's own mean.

    Grouping by service (not global) matters: a $2,000/day GPU cluster
    and a $5/day storage bucket don't share a baseline.
    """
    df = df.copy()
    df["z"] = df.groupby("service")["cost"].transform(
        lambda s: (s - s.mean()) / s.std(ddof=0)
    )
    df["z"] = df["z"].fillna(0)
    return df[df["z"].abs() > z_thresh].sort_values("z", ascending=False)
