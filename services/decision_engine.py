class DecisionEngine:

    def build_decision(
        self,
        analysis: dict,
        optimization: dict
    ) -> dict:

        # Check whether the optimizer actually found a solution
        if optimization.get("status") != "OPTIMAL":
            return {
                "decision_type": "NO_ACTION",
                "priority": "low",
                "evidence_strength": "low",
                "reason": "The optimization engine did not return an optimal solution."
            }

        # Never recommend a schedule that violates constraints
        if not optimization.get("all_constraints_satisfied", False):
            return {
                "decision_type": "NO_ACTION",
                "priority": "low",
                "evidence_strength": "low",
                "reason": "The optimized schedule did not satisfy all operational constraints."
            }

        savings = optimization.get("savings", {})

        daily_cost_saving = float(
            savings.get("daily_cost_inr", 0)
        )

        energy_saving = float(
            savings.get("energy_kwh", 0)
        )

        peak_reduction = float(
            savings.get("peak_reduction_kw", 0)
        )

        anomaly_status = analysis.get(
            "anomaly_status",
            "Unknown"
        )

        # No meaningful economic or energy benefit
        if daily_cost_saving <= 0 and energy_saving <= 0 and peak_reduction <= 0:
            return {
                "decision_type": "MONITOR",
                "priority": "low",
                "evidence_strength": "medium",
                "reason": (
                    "The optimizer did not identify a meaningful "
                    "energy, peak-demand, or cost improvement."
                )
            }

        # Anomalous demand deserves the highest priority
        if anomaly_status == "Anomalous":
            decision_type = "PRIORITIZE"
            priority = "high"

        elif anomaly_status == "Elevated":
            decision_type = "OPTIMIZE"
            priority = "medium"

        else:
            decision_type = "OPTIMIZE"
            priority = "medium"

        return {
            "decision_type": decision_type,
            "priority": priority,
            "evidence_strength": "high",
            "reason": (
                "The optimizer identified a feasible schedule "
                "with measurable energy, peak-demand, or cost benefits."
            ),
            "daily_cost_saving_inr": round(daily_cost_saving, 2),
            "energy_saving_kwh": round(energy_saving, 2),
            "peak_reduction_kw": round(peak_reduction, 2),
            "anomaly_status": anomaly_status
        }