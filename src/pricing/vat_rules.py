from typing import Dict, Tuple
from enum import Enum


class VATCategory(Enum):
    STANDARD = "standard"
    INTERMEDIATE = "intermediate"
    REDUCED = "reduced"


class VATCalculator:
    def __init__(self):
        self.rates = {
            VATCategory.STANDARD: 0.20,
            VATCategory.INTERMEDIATE: 0.10,
            VATCategory.REDUCED: 0.055
        }

        self.energy_renovation_tasks = {
            "insulation", "ventilation", "heating", "boiler",
            "thermodynamic water heater", "renewable energy",
            "heat pump", "solar", "energy efficiency"
        }

        self.gas_oil_boiler_tasks = {
            "gas boiler", "oil boiler", "fuel boiler"
        }

    def calculate_vat(self, task_name: str, subtotal: float,
                      project_context: Dict = None) -> Tuple[float, float]:
        if project_context is None:
            project_context = {}

        vat_rate = self._determine_vat_rate(task_name, project_context)
        vat_amount = subtotal * vat_rate

        return vat_rate, vat_amount

    def _determine_vat_rate(self, task_name: str, context: Dict) -> float:
        building_age = context.get("building_age_years", 10)
        work_type = context.get("work_type", "renovation")
        area_increase = context.get("area_increase_percent", 0)

        if self._is_new_construction(work_type, area_increase):
            return self.rates[VATCategory.STANDARD]

        if building_age < 2:
            return self.rates[VATCategory.STANDARD]

        if self._is_gas_oil_boiler(task_name):
            return self.rates[VATCategory.STANDARD]

        if self._is_energy_renovation(task_name, context):
            return self.rates[VATCategory.REDUCED]

        if self._is_renovation_work(area_increase):
            return self.rates[VATCategory.INTERMEDIATE]

        return self.rates[VATCategory.STANDARD]

    def _is_new_construction(self, work_type: str, area_increase: float) -> bool:
        return (work_type.lower() in ["new construction", "extension"] or
                area_increase > 10)

    def _is_energy_renovation(self, task_name: str, context: Dict) -> bool:
        task_lower = task_name.lower()
        description = context.get("project_description", "").lower()

        for energy_task in self.energy_renovation_tasks:
            if energy_task in task_lower or energy_task in description:
                return True

        return False

    def _is_gas_oil_boiler(self, task_name: str) -> bool:
        task_lower = task_name.lower()
        return any(boiler_type in task_lower for boiler_type in self.gas_oil_boiler_tasks)

    def _is_renovation_work(self, area_increase: float) -> bool:
        return area_increase <= 10

    def get_vat_summary(self, tasks: list, project_context: Dict = None) -> Dict:
        if project_context is None:
            project_context = {}

        summary = {
            "tasks": [],
            "total_before_vat": 0.0,
            "total_vat": 0.0,
            "total_with_vat": 0.0,
            "vat_breakdown": {
                "standard_rate": {"subtotal": 0.0, "vat": 0.0},
                "intermediate_rate": {"subtotal": 0.0, "vat": 0.0},
                "reduced_rate": {"subtotal": 0.0, "vat": 0.0}
            }
        }

        for task in tasks:
            task_subtotal = task.labor.total + \
                sum(mat.total for mat in task.materials)
            vat_rate, vat_amount = self.calculate_vat(
                task.name, task_subtotal, project_context)

            task_info = {
                "task_name": task.name,
                "subtotal": task_subtotal,
                "vat_rate": vat_rate,
                "vat_amount": vat_amount,
                "total": task_subtotal + vat_amount
            }

            summary["tasks"].append(task_info)
            summary["total_before_vat"] += task_subtotal
            summary["total_vat"] += vat_amount

            if vat_rate == 0.20:
                summary["vat_breakdown"]["standard_rate"]["subtotal"] += task_subtotal
                summary["vat_breakdown"]["standard_rate"]["vat"] += vat_amount
            elif vat_rate == 0.10:
                summary["vat_breakdown"]["intermediate_rate"]["subtotal"] += task_subtotal
                summary["vat_breakdown"]["intermediate_rate"]["vat"] += vat_amount
            elif vat_rate == 0.055:
                summary["vat_breakdown"]["reduced_rate"]["subtotal"] += task_subtotal
                summary["vat_breakdown"]["reduced_rate"]["vat"] += vat_amount

        summary["total_with_vat"] = summary["total_before_vat"] + \
            summary["total_vat"]
        return summary

    def explain_vat_rate(self, task_name: str, vat_rate: float, context: Dict = None) -> str:
        if context is None:
            context = {}

        if vat_rate == 0.055:
            return "5.5% VAT applied - Energy-efficiency renovation work"
        elif vat_rate == 0.10:
            return "10% VAT applied - Renovation work on building over 2 years old"
        elif vat_rate == 0.20:
            if self._is_gas_oil_boiler(task_name):
                return "20% VAT applied - Gas/oil boiler installation (March 2025 rule)"
            elif self._is_new_construction(context.get("work_type", ""), context.get("area_increase_percent", 0)):
                return "20% VAT applied - New construction or major extension"
            else:
                return "20% VAT applied - Standard rate"
        else:
            return f"{vat_rate*100:.1f}% VAT applied"
