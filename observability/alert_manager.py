"""
alert_manager.py
Formats structured observability output into the 🚨 DEFENSE FAILURE card
shown in the dashboard and printed to console during run_demo.py.
"""

from dataclasses import dataclass, asdict


@dataclass
class DefenseFailureAlert:
    round_num: int
    attack_type: str
    failed_layer: str
    what_happened: str
    why: str
    impact: str
    remediation: str
    status: str = "🔴 Requires retraining"

    def to_dict(self) -> dict:
        return asdict(self)

    def to_card_text(self) -> str:
        attack_label = self.attack_type.replace("_", " ").title()
        return (
            "🚨 DEFENSE FAILURE\n\n"
            f"Attack: {attack_label}\n"
            f"Round: {self.round_num}\n\n"
            "Where:\n"
            f"{self.failed_layer}\n\n"
            "What happened:\n"
            f"{self.what_happened}\n\n"
            "Why:\n"
            f"{self.why}\n\n"
            "Impact:\n"
            f"{self.impact}\n\n"
            "Recommended remediation:\n"
            f"{self.remediation}\n\n"
            "Status:\n"
            f"{self.status}"
        )


def build_alert(round_num: int, attack_type: str, missed_count: int, total_count: int,
                 root_cause: dict, remediation_text: str) -> DefenseFailureAlert:
    weak_feats = ", ".join(f for f, _ in root_cause["weak_features"][:2]) or "the layer's primary features"

    return DefenseFailureAlert(
        round_num=round_num,
        attack_type=attack_type,
        failed_layer=root_cause["failed_layer"],
        what_happened=(
            f"{missed_count} of {total_count} {attack_type.replace('_',' ')} transactions "
            f"were scored below the detection threshold."
        ),
        why=root_cause["explanation"],
        impact="Attack classified as legitimate.",
        remediation=remediation_text,
    )
