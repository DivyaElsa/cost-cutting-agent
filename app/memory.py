from hindsight_client import Hindsight


class CostMemory:
    """Wraps the Hindsight client with FinOps-specific conventions.

    One bank per team, so a data-science cost decision never bleeds
    into growth's memory.
    """

    def __init__(self, base_url: str = "http://localhost:8888"):
        self.client = Hindsight(base_url=base_url)

    def bank_id(self, team: str) -> str:
        return f"finops-{team}"

    def recall_context(self, team: str, service: str) -> list:
        return self.client.recall(
            bank_id=self.bank_id(team),
            query=f"cost spike or suggestion for {service}",
        )

    def reflect_on_team(self, team: str) -> str:
        return self.client.reflect(
            bank_id=self.bank_id(team),
            query=f"What cost patterns and rejected suggestions does {team} have?",
        )

    def retain_decision(
        self, team: str, service: str, suggestion: str, accepted: bool, saving: float = 0.0
    ):
        outcome = "accepted" if accepted else "rejected"
        self.client.retain(
            bank_id=self.bank_id(team),
            content=(
                f"{service}: suggestion '{suggestion}' was {outcome}. "
                f"Monthly saving: ${saving:.2f}"
            ),
            context="finops-decision",
        )

    def retain_anomaly(self, team: str, service: str, cost: float, z: float):
        self.client.retain(
            bank_id=self.bank_id(team),
            content=f"{service} cost anomaly detected: ${cost:.2f} (z-score {z:.2f})",
            context="finops-anomaly",
        )
