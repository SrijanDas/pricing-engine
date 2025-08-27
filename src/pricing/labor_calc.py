from typing import Dict, Tuple
from src.models import Labor, TaskType


class LaborCalculator:
    def __init__(self):
        self.base_rates = self._initialize_rates()
        self.task_estimates = self._initialize_task_estimates()
        self.skill_multipliers = {
            "unskilled": 0.7,
            "semi-skilled": 1.0,
            "skilled": 1.3,
            "specialist": 1.6
        }

    def _initialize_rates(self) -> Dict[str, float]:
        return {
            "unskilled": 25.0,     # €/hour - basic demolition, cleaning
            "semi-skilled": 35.0,  # €/hour - painting, basic installations
            "skilled": 45.0,       # €/hour - plumbing, electrical, tiling
            "specialist": 65.0     # €/hour - complex technical work
        }

    def _initialize_task_estimates(self) -> Dict[str, Dict]:
        return {
            "demolition": {
                "hours_per_m2": 0.8,
                "base_hours": 4.0,
                "skill_level": "unskilled",
                "workers_needed": 1,
                "complexity_factors": {
                    "simple": 1.0,
                    "moderate": 1.3,
                    "complex": 1.8
                }
            },
            "tile_removal": {
                "hours_per_m2": 1.2,
                "base_hours": 2.0,
                "skill_level": "semi-skilled",
                "workers_needed": 1,
                "complexity_factors": {
                    "simple": 1.0,
                    "moderate": 1.4,
                    "complex": 2.0
                }
            },
            "plumbing": {
                "hours_per_fixture": 6.0,
                "base_hours": 8.0,
                "skill_level": "skilled",
                "workers_needed": 1,
                "complexity_factors": {
                    "simple": 1.0,      # Replace like-for-like
                    "moderate": 1.5,    # Move fixtures
                    "complex": 2.2      # New plumbing runs
                }
            },
            "electrical": {
                "hours_per_point": 2.0,
                "base_hours": 4.0,
                "skill_level": "skilled",
                "workers_needed": 1,
                "complexity_factors": {
                    "simple": 1.0,      # Replace fixtures
                    "moderate": 1.6,    # Add new circuits
                    "complex": 2.5      # Complete rewiring
                }
            },
            "tiling": {
                "hours_per_m2": 2.5,
                "base_hours": 4.0,
                "skill_level": "skilled",
                "workers_needed": 1,
                "complexity_factors": {
                    "simple": 1.0,      # Straight lay, large tiles
                    "moderate": 1.4,    # Pattern work, medium tiles
                    "complex": 1.8      # Intricate patterns, small tiles
                }
            },
            "painting": {
                "hours_per_m2": 0.6,
                "base_hours": 2.0,
                "skill_level": "semi-skilled",
                "workers_needed": 1,
                "complexity_factors": {
                    "simple": 1.0,      # Single coat, simple prep
                    "moderate": 1.3,    # Two coats, medium prep
                    "complex": 1.6      # Multiple coats, extensive prep
                }
            },
            "flooring": {
                "hours_per_m2": 1.8,
                "base_hours": 3.0,
                "skill_level": "skilled",
                "workers_needed": 1,
                "complexity_factors": {
                    "simple": 1.0,      # Straight lay
                    "moderate": 1.3,    # Pattern or cuts needed
                    "complex": 1.7      # Complex patterns, many cuts
                }
            },
            "waterproofing": {
                "hours_per_m2": 1.0,
                "base_hours": 4.0,
                "skill_level": "specialist",
                "workers_needed": 1,
                "complexity_factors": {
                    "simple": 1.0,
                    "moderate": 1.2,
                    "complex": 1.5
                }
            },
            "fixture_installation": {
                "hours_per_fixture": 3.0,
                "base_hours": 2.0,
                "skill_level": "skilled",
                "workers_needed": 1,
                "complexity_factors": {
                    "simple": 1.0,      # Standard installation
                    "moderate": 1.4,    # Custom fitting required
                    "complex": 1.8      # Structural modifications needed
                }
            }
        }

    def calculate_labor(self, task_name: str, area: float = 4.0,
                        complexity: str = "moderate",
                        urgency_factor: float = 1.0) -> Labor:

        task_key = self._normalize_task_name(task_name)

        if task_key not in self.task_estimates:
            return self._default_labor_estimate(task_name, area)

        task_data = self.task_estimates[task_key]
        skill_level = task_data["skill_level"]
        base_rate = self.base_rates[skill_level]

        hours = self._calculate_hours(task_key, area, complexity, task_data)

        adjusted_rate = base_rate * urgency_factor

        total = hours * adjusted_rate

        return Labor(
            hours=hours,
            rate=adjusted_rate,
            total=total,
            skill_level=skill_level,
            workers_needed=task_data["workers_needed"]
        )

    def _normalize_task_name(self, task_name: str) -> str:
        task_name_lower = task_name.lower()

        # Map common variations to standard keys
        mapping = {
            "remove tiles": "tile_removal",
            "tile removal": "tile_removal",
            "remove old tiles": "tile_removal",
            "demolition": "demolition",
            "demo": "demolition",
            "plumbing work": "plumbing",
            "plumber": "plumbing",
            "redo plumbing": "plumbing",
            "electrical work": "electrical",
            "electrician": "electrical",
            "rewiring": "electrical",
            "tiling": "tiling",
            "tile installation": "tiling",
            "lay tiles": "tiling",
            "painting": "painting",
            "paint": "painting",
            "repaint": "painting",
            "flooring": "flooring",
            "floor installation": "flooring",
            "lay flooring": "flooring",
            "waterproofing": "waterproofing",
            "waterproof": "waterproofing",
            "install fixtures": "fixture_installation",
            "fixture installation": "fixture_installation",
            "install vanity": "fixture_installation",
            "install toilet": "fixture_installation"
        }

        return mapping.get(task_name_lower, task_name_lower)

    def _calculate_hours(self, task_key: str, area: float,
                         complexity: str, task_data: Dict) -> float:

        base_hours = task_data["base_hours"]
        complexity_multiplier = task_data["complexity_factors"].get(
            complexity, 1.3)

        if "hours_per_m2" in task_data:
            variable_hours = task_data["hours_per_m2"] * area
        elif "hours_per_fixture" in task_data:
            fixtures = max(1, int(area / 2))  # Rough estimate
            variable_hours = task_data["hours_per_fixture"] * fixtures
        elif "hours_per_point" in task_data:
            points = max(2, int(area))  # Minimum 2 points
            variable_hours = task_data["hours_per_point"] * points
        else:
            # Fixed time tasks
            variable_hours = 0

        total_hours = (base_hours + variable_hours) * complexity_multiplier
        return round(total_hours, 1)

    def _default_labor_estimate(self, task_name: str, area: float) -> Labor:
        hours = max(4.0, area * 1.5)
        rate = self.base_rates["skilled"]
        total = hours * rate

        return Labor(
            hours=hours,
            rate=rate,
            total=total,
            skill_level="skilled",
            workers_needed=1
        )

    def estimate_project_duration(self, tasks: list, overlap_factor: float = 0.7) -> str:
        total_hours = sum(task.labor.hours for task in tasks)

        effective_hours = total_hours * overlap_factor

        # Convert to working days (8 hours per day)
        days = effective_hours / 8

        if days <= 1:
            return "1 day"
        elif days <= 2:
            return "1-2 days"
        elif days <= 5:
            return f"{int(days)}-{int(days)+1} days"
        elif days <= 10:
            return f"1-2 weeks"
        else:
            return f"{int(days/5)}-{int(days/5)+1} weeks"

    def get_skill_requirements(self, task_name: str) -> Tuple[str, int]:
        task_key = self._normalize_task_name(task_name)

        if task_key in self.task_estimates:
            task_data = self.task_estimates[task_key]
            return task_data["skill_level"], task_data["workers_needed"]

        return "skilled", 1  # Default

    def calculate_rush_surcharge(self, base_cost: float, urgency: str) -> float:
        multipliers = {
            "standard": 1.0,
            "urgent": 1.25,      # 25% surcharge
            "emergency": 1.5     # 50% surcharge
        }

        return base_cost * multipliers.get(urgency, 1.0)
