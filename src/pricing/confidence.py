from typing import Dict, List, Tuple
import math


class ConfidenceScorer:
    def __init__(self):
        self.scoring_weights = {
            "input_clarity": 0.40,
            "material_availability": 0.30,
            "labor_accuracy": 0.30
        }

        self.risk_factors = self._initialize_risk_factors()
        self.confidence_thresholds = {
            "very_high": 0.9,
            "high": 0.8,
            "medium": 0.7,
            "low": 0.6,
            "very_low": 0.0
        }

    def _initialize_risk_factors(self) -> Dict[str, Dict]:
        return {
            "input_risks": {
                "unclear_requirements": -0.2,
                "missing_dimensions": -0.15,
                "ambiguous_materials": -0.1,
                "incomplete_description": -0.1,
                "conflicting_information": -0.25
            },
            "market_risks": {
                "material_shortage": -0.15,
                "seasonal_demand": -0.05,
                "labor_shortage": -0.1,
                "price_volatility": -0.08,
                "new_regulations": -0.12
            },
            "project_risks": {
                "high_complexity": -0.1,
                "tight_timeline": -0.08,
                "budget_constraints": -0.05,
                "access_difficulties": -0.07,
                "structural_unknowns": -0.15
            },
            "data_quality_risks": {
                "outdated_prices": -0.1,
                "limited_local_data": -0.12,
                "no_historical_benchmarks": -0.08,
                "unverified_suppliers": -0.06
            }
        }

    def calculate_confidence(self, assessment_data: Dict) -> Tuple[float, Dict]:
        scores = {}

        scores["input_clarity"] = self._score_input_clarity(assessment_data)

        scores["material_availability"] = self._score_material_availability(
            assessment_data)

        scores["labor_accuracy"] = self._score_labor_accuracy(assessment_data)

        overall_score = sum(
            scores[factor] * weight
            for factor, weight in self.scoring_weights.items()
        )

        risk_adjustment = self._calculate_risk_adjustment(assessment_data)
        overall_score = max(0.0, min(1.0, overall_score + risk_adjustment))

        breakdown = {
            "overall_score": round(overall_score, 3),
            "component_scores": {k: round(v, 3) for k, v in scores.items()},
            "risk_adjustment": round(risk_adjustment, 3),
            "confidence_level": self._get_confidence_level(overall_score),
            "recommendations": self._get_recommendations(overall_score, scores, assessment_data)
        }

        return overall_score, breakdown

    def _score_input_clarity(self, data: Dict) -> float:
        clarity_factors = {
            "has_dimensions": data.get("room_dimensions", False),
            "clear_task_description": data.get("task_clarity_score", 0.5),
            "specific_materials": data.get("material_specificity", 0.5),
            "budget_indication": data.get("has_budget_info", False),
            "timeline_specified": data.get("has_timeline", False)
        }

        base_score = data.get("transcript_clarity", 0.7)

        completeness_bonus = sum([
            0.1 if clarity_factors["has_dimensions"] else 0,
            0.1 if clarity_factors["budget_indication"] else 0,
            0.05 if clarity_factors["timeline_specified"] else 0
        ])

        clarity_adjustment = (
            clarity_factors["clear_task_description"] - 0.5) * 0.2

        return min(1.0, base_score + completeness_bonus + clarity_adjustment)

    def _score_material_availability(self, data: Dict) -> float:
        materials = data.get("materials_list", [])

        if not materials:
            return 0.5  # Neutral if no specific materials

        availability_scores = []

        for material in materials:
            availability = material.get("availability_score", 0.9)
            price_stability = material.get("price_stability", 0.8)
            supplier_reliability = material.get("supplier_reliability", 0.85)

            material_score = (
                availability * 0.5 + price_stability * 0.3 + supplier_reliability * 0.2)
            availability_scores.append(material_score)

        return sum(availability_scores) / len(availability_scores)

    def _score_labor_accuracy(self, data: Dict) -> float:
        factors = {
            "task_standardization": data.get("task_standardization_score", 0.8),
            "complexity_assessment": data.get("complexity_accuracy", 0.7),
            "local_labor_data": data.get("has_local_labor_rates", True),
            "skill_requirements_clear": data.get("skill_requirements_clarity", 0.8)
        }

        base_score = factors["task_standardization"]

        complexity_adj = (factors["complexity_assessment"] - 0.5) * 0.2

        local_bonus = 0.1 if factors["local_labor_data"] else -0.1

        skill_adj = (factors["skill_requirements_clear"] - 0.5) * 0.1

        return max(0.0, min(1.0, base_score + complexity_adj + local_bonus + skill_adj))

    def _calculate_risk_adjustment(self, data: Dict) -> float:
        total_adjustment = 0.0

        for risk_category, risk_factors in self.risk_factors.items():
            category_risks = data.get(f"{risk_category}_detected", [])

            for risk in category_risks:
                if risk in risk_factors:
                    total_adjustment += risk_factors[risk]

        return total_adjustment

    def _get_confidence_level(self, score: float) -> str:
        if score >= self.confidence_thresholds["very_high"]:
            return "Very High"
        elif score >= self.confidence_thresholds["high"]:
            return "High"
        elif score >= self.confidence_thresholds["medium"]:
            return "Medium"
        elif score >= self.confidence_thresholds["low"]:
            return "Low"
        else:
            return "Very Low"

    def _get_recommendations(self, score: float, component_scores: Dict, data: Dict) -> List[str]:
        recommendations = []

        if score < 0.6:
            recommendations.append(
                "Recommend site visit before finalizing quote")
            recommendations.append(
                "Request additional project details from client")
        elif score < 0.7:
            recommendations.append("Consider adding contingency margin")
            recommendations.append(
                "Verify material specifications with client")
        elif score < 0.8:
            recommendations.append("Quote ready with minor clarifications")

        if component_scores.get("input_clarity", 0) < 0.7:
            recommendations.append("Request clearer project specifications")

        if component_scores.get("material_availability", 0) < 0.8:
            recommendations.append(
                "Verify current material prices and availability")

        if component_scores.get("labor_accuracy", 0) < 0.75:
            recommendations.append(
                "Consider getting second opinion on labor estimates")

        location = data.get("location", "").lower()
        if location in ["paris", "nice", "cannes"]:
            if score < 0.8:
                recommendations.append(
                    "Premium market - ensure quality standards alignment")

        return list(set(recommendations))

    def assess_quote_risk(self, quote_data: Dict) -> Dict[str, any]:
        confidence_score = quote_data.get("global_confidence_score", 0.5)
        project_value = quote_data.get("grand_total", 0)

        if confidence_score >= 0.9:
            risk_level = "Very Low"
            risk_color = "green"
        elif confidence_score >= 0.8:
            risk_level = "Low"
            risk_color = "lightgreen"
        elif confidence_score >= 0.7:
            risk_level = "Medium"
            risk_color = "yellow"
        elif confidence_score >= 0.6:
            risk_level = "High"
            risk_color = "orange"
        else:
            risk_level = "Very High"
            risk_color = "red"

        potential_variance = self._calculate_potential_variance(
            confidence_score, project_value)

        return {
            "risk_level": risk_level,
            "risk_color": risk_color,
            "confidence_score": confidence_score,
            "potential_variance": potential_variance,
            "recommended_action": self._get_risk_action(risk_level),
            "contingency_suggestion": self._suggest_contingency(confidence_score)
        }

    def _calculate_potential_variance(self, confidence_score: float, project_value: float) -> Dict[str, float]:
        variance_factor = 1 - confidence_score

        potential_overrun = project_value * variance_factor * 0.3  # Max 30% overrun
        potential_saving = project_value * variance_factor * 0.1   # Max 10% saving

        return {
            "potential_overrun": potential_overrun,
            "potential_saving": potential_saving,
            "variance_range": f"-{potential_saving:.0f}€ to +{potential_overrun:.0f}€"
        }

    def _get_risk_action(self, risk_level: str) -> str:
        actions = {
            "Very Low": "Proceed with quote as-is",
            "Low": "Proceed with minor review",
            "Medium": "Review and add 5-10% contingency",
            "High": "Detailed review required, consider site visit",
            "Very High": "Do not quote without additional information"
        }
        return actions.get(risk_level, "Review required")

    def _suggest_contingency(self, confidence_score: float) -> str:
        if confidence_score >= 0.9:
            return "0-5% contingency recommended"
        elif confidence_score >= 0.8:
            return "5-10% contingency recommended"
        elif confidence_score >= 0.7:
            return "10-15% contingency recommended"
        elif confidence_score >= 0.6:
            return "15-20% contingency recommended"
        else:
            return "20%+ contingency required or decline quote"
