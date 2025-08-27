import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional
from src.models import Quote, Zone, Task, TaskType, TranscriptAnalysis
from src.pricing.material_db import MaterialDatabase
from src.pricing.labor_calc import LaborCalculator
from src.pricing.vat_rules import VATCalculator
from src.pricing.confidence import ConfidenceScorer
from src.transcript.analyzer import TranscriptAnalyzer
from src.openai_client import openai_client, DEFAULT_MODEL


class DonizoPricingEngine:
    def __init__(self):
        self.material_db = MaterialDatabase()
        self.labor_calc = LaborCalculator()
        self.vat_calc = VATCalculator()
        self.confidence_scorer = ConfidenceScorer()
        self.transcript_analyzer = TranscriptAnalyzer()

    def generate_quote_from_transcript(self, transcript: str,
                                       override_location: Optional[str] = None) -> Quote:
        analysis = self.transcript_analyzer.analyze_transcript(transcript)
        if override_location:
            analysis.location = override_location

        project_context = {
            "location": analysis.location,
            "project_description": transcript,
            "budget_preference": analysis.budget_preference,
            "special_requirements": analysis.special_requirements,
            "building_age_years": 10,
            "room_size": analysis.room_size
        }

        tasks = self._generate_tasks(
            analysis, project_context)

        bathroom_zone = Zone(
            name="bathroom",
            area=analysis.room_size,
            tasks=tasks,
            zone_total=sum(task.total_price for task in tasks),
            zone_confidence=sum(
                task.confidence_score for task in tasks) / len(tasks) if tasks else 0.5
        )

        total_before_vat = sum(task.subtotal for task in tasks)
        total_vat = sum(task.vat_amount for task in tasks)
        grand_total = total_before_vat + total_vat

        confidence_data = self._prepare_confidence_data(
            analysis, tasks, project_context)
        global_confidence, confidence_breakdown = self.confidence_scorer.calculate_confidence(
            confidence_data)

        quote = Quote(
            quote_id=str(uuid.uuid4()),
            client_location=analysis.location,
            project_summary=self._create_project_summary(analysis),
            zones={"bathroom": bathroom_zone},
            global_confidence_score=global_confidence,
            total_before_vat=total_before_vat,
            total_vat=total_vat,
            grand_total=grand_total
        )

        return quote

    def _generate_tasks(self, analysis: TranscriptAnalysis,
                        project_context: Dict) -> List[Task]:
        tasks = []

        task_mappings = self._map_tasks_with_openai(analysis.tasks_identified)

        for task_name in analysis.tasks_identified:
            task_mapping = task_mappings.get(task_name)
            if task_mapping:
                task_key = task_mapping["task_key"]
                task_type = TaskType(task_mapping["task_type"])
            else:
                task_key = task_name.lower()
                task_type = TaskType.FIXTURES

            task = self._create_task(
                name=task_name,
                task_type=task_type,
                task_key=task_key,
                analysis=analysis,
                project_context=project_context
            )

            if task:
                tasks.append(task)

        if not tasks:
            default_tasks = self._generate_default_tasks_with_openai(analysis)

            for task_name, task_key, task_type in default_tasks:
                task = self._create_task(
                    name=task_name,
                    task_type=task_type,
                    task_key=task_key,
                    analysis=analysis,
                    project_context=project_context
                )
                if task:
                    tasks.append(task)

        return tasks

    def _map_tasks_with_openai(self, task_names: List[str]) -> Dict[str, Dict[str, str]]:
        if not task_names:
            return {}

        try:
            # Define available task types from the enum
            available_task_types = [task_type.value for task_type in TaskType]

            system_prompt = f"""
You are an expert renovation task classifier for Donizo, a French renovation company.
Your job is to map renovation task names to standardized task types and keys.

Available task types: {', '.join(available_task_types)}

For each task name provided, return a JSON object with:
- task_key: a standardized internal key (lowercase, underscore-separated)
- task_type: one of the available task types above

Guidelines:
- Use the most appropriate task type from the available options
- task_key should be a clean, standardized version suitable for internal processing
- If a task doesn't fit perfectly, choose the closest match
- For demolition tasks: use "demolition" 
- For plumbing tasks: use "plumbing"
- For electrical tasks: use "electrical"
- For tiling/ceramic work: use "tiling"
- For painting: use "painting"
- For flooring installation: use "flooring"
- For fixture installation: use "fixtures"
- For waterproofing: use "waterproofing"

Respond with a JSON object where each key is the original task name and the value is an object with task_key and task_type.
"""

            user_prompt = f"""
Please classify these renovation tasks:
{json.dumps(task_names)}

Return only valid JSON.
"""

            response = openai_client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )

            response_text = response.choices[0].message.content

            # Parse JSON response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                return json.loads(response_text)

        except Exception as e:
            print(f"Error mapping tasks with OpenAI: {e}")
            # Fallback to simple mapping
            return self._fallback_task_mapping(task_names)

    def _generate_default_tasks_with_openai(self, analysis: TranscriptAnalysis) -> List[tuple]:
        try:
            available_task_types = [task_type.value for task_type in TaskType]

            system_prompt = f"""
You are an expert renovation planner for Donizo, a French renovation company.
Based on the project context, suggest appropriate renovation tasks.

Available task types: {', '.join(available_task_types)}

Return a JSON array of task objects, each with:
- name: descriptive task name (in English)
- task_key: standardized internal key (lowercase, underscore-separated)  
- task_type: one of the available task types

Consider:
- Room type and size
- Budget preference
- Typical renovation workflow
- French renovation standards
- Logical task sequence

Suggest 4-6 essential tasks for a typical renovation.
"""

            user_prompt = f"""
Generate default renovation tasks for this project:
- Room: {analysis.room_type} ({analysis.room_size}sqm)
- Location: {analysis.location}
- Budget: {analysis.budget_preference}
- Special requirements: {analysis.special_requirements}

Return only a JSON array.
"""

            response = openai_client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )

            response_text = response.choices[0].message.content

            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                tasks_data = json.loads(json_text)

                return [
                    (task["name"], task["task_key"],
                     TaskType(task["task_type"]))
                    for task in tasks_data
                ]
            else:
                tasks_data = json.loads(response_text)
                return [
                    (task["name"], task["task_key"],
                     TaskType(task["task_type"]))
                    for task in tasks_data
                ]

        except Exception as e:
            print(f"Error generating default tasks with OpenAI: {e}")
            return [
                ("Remove old tiles", "demolition", TaskType.DEMOLITION),
                ("Plumbing work", "plumbing", TaskType.PLUMBING),
                ("Install new tiles", "tiling", TaskType.TILING),
                ("Paint walls", "painting", TaskType.PAINTING),
                ("Install fixtures", "fixtures", TaskType.FIXTURES)
            ]

    def _fallback_task_mapping(self, task_names: List[str]) -> Dict[str, Dict[str, str]]:
        fallback_mapping = {
            "remove tiles": {"task_key": "demolition", "task_type": "demolition"},
            "tile removal": {"task_key": "demolition", "task_type": "demolition"},
            "demolition": {"task_key": "demolition", "task_type": "demolition"},
            "plumbing": {"task_key": "plumbing", "task_type": "plumbing"},
            "plumbing work": {"task_key": "plumbing", "task_type": "plumbing"},
            "redo plumbing": {"task_key": "plumbing", "task_type": "plumbing"},
            "electrical": {"task_key": "electrical", "task_type": "electrical"},
            "electrical work": {"task_key": "electrical", "task_type": "electrical"},
            "tiling": {"task_key": "tiling", "task_type": "tiling"},
            "tile installation": {"task_key": "tiling", "task_type": "tiling"},
            "lay tiles": {"task_key": "tiling", "task_type": "tiling"},
            "painting": {"task_key": "painting", "task_type": "painting"},
            "paint": {"task_key": "painting", "task_type": "painting"},
            "repaint": {"task_key": "painting", "task_type": "painting"},
            "flooring": {"task_key": "flooring", "task_type": "flooring"},
            "install fixtures": {"task_key": "fixtures", "task_type": "fixtures"},
            "fixture installation": {"task_key": "fixtures", "task_type": "fixtures"},
            "install vanity": {"task_key": "fixtures", "task_type": "fixtures"},
            "install toilet": {"task_key": "fixtures", "task_type": "fixtures"}
        }

        result = {}
        for task_name in task_names:
            mapping = fallback_mapping.get(task_name.lower())
            if mapping:
                result[task_name] = mapping
            else:
                # Default mapping for unknown tasks
                result[task_name] = {
                    "task_key": task_name.lower(), "task_type": "fixtures"}

        return result

    def _create_task(self, name: str, task_type: TaskType, task_key: str,
                     analysis: TranscriptAnalysis,
                     project_context: Dict) -> Optional[Task]:
        try:
            complexity = self._determine_task_complexity(task_key, analysis)
            labor = self.labor_calc.calculate_labor(
                task_name=task_key,
                area=analysis.room_size,
                complexity=complexity,
                urgency_factor=1.0
            )

            budget_level = self._map_budget_to_variant(
                analysis.budget_preference)
            materials = self.material_db.get_task_materials(
                task_type=task_key,
                area=analysis.room_size,
                budget_level=budget_level
            )

            material_total = sum(material.total for material in materials)
            subtotal = labor.total + material_total

            vat_rate, vat_amount = self.vat_calc.calculate_vat(
                task_key, subtotal, project_context)

            margin = self._calculate_margin(
                subtotal, complexity, analysis.budget_preference)
            subtotal_with_margin = subtotal * (1 + margin)
            vat_amount_with_margin = vat_amount * (1 + margin)
            total_price = subtotal_with_margin + vat_amount_with_margin

            task_confidence = self._calculate_task_confidence(
                task_key, materials, labor)

            duration = self.labor_calc.estimate_project_duration(
                [type('Task', (), {'labor': labor})()])

            vat_percentage = f"{vat_rate * 100:.1f}%"

            return Task(
                name=name,
                task_type=task_type,
                description=f"{name} for {analysis.room_size}sqm bathroom",
                labor=labor,
                materials=materials,
                estimated_duration=duration,
                vat_rate=vat_rate,
                vat_percentage=vat_percentage,
                subtotal=subtotal_with_margin,
                vat_amount=vat_amount_with_margin,
                total_price=total_price,
                margin=margin,
                confidence_score=task_confidence,
                complexity_factor=self._get_complexity_multiplier(complexity)
            )

        except Exception as e:
            print(f"Error creating task {name}: {e}")
            return None

    def _determine_task_complexity(self, task_key: str, analysis: TranscriptAnalysis) -> str:
        complexity_indicators = {
            "simple": 0,
            "moderate": 1,
            "complex": 2
        }

        complexity_score = 1

        if analysis.room_size > 6:
            complexity_score += 1
        elif analysis.room_size < 3:
            complexity_score += 0.5

        if analysis.budget_preference in ["premium", "luxury"]:
            complexity_score += 1

        if analysis.special_requirements:
            complexity_score += 0.5

        complex_tasks = ["plumbing", "electrical", "waterproofing"]
        if task_key in complex_tasks:
            complexity_score += 0.5

        if complexity_score >= 2.5:
            return "complex"
        elif complexity_score >= 1.5:
            return "moderate"
        else:
            return "simple"

    def _map_budget_to_variant(self, budget_preference: str) -> str:
        mapping = {
            "budget-conscious": "basic",
            "moderate": "basic",
            "premium": "premium",
            "luxury": "luxury"
        }
        return mapping.get(budget_preference, "basic")

    def _calculate_margin(self, subtotal: float, complexity: str, budget_preference: str) -> float:
        base_margin = 0.15

        complexity_adjustments = {
            "simple": 0.0,
            "moderate": 0.02,
            "complex": 0.05
        }

        budget_adjustments = {
            "budget-conscious": -0.02,
            "moderate": 0.0,
            "premium": 0.05,
            "luxury": 0.10
        }

        margin = base_margin
        margin += complexity_adjustments.get(complexity, 0.02)
        margin += budget_adjustments.get(budget_preference, 0.0)

        return max(0.15, min(0.30, margin))

    def _get_complexity_multiplier(self, complexity: str) -> float:
        multipliers = {
            "simple": 1.0,
            "moderate": 1.2,
            "complex": 1.5
        }
        return multipliers.get(complexity, 1.2)

    def _calculate_task_confidence(self, task_key: str, materials: List, labor) -> float:
        base_confidence = {
            "painting": 0.9,
            "demolition": 0.85,
            "tiling": 0.8,
            "fixtures": 0.75,
            "plumbing": 0.7,
            "electrical": 0.7,
            "waterproofing": 0.65
        }.get(task_key, 0.75)

        if materials:
            avg_availability = sum(
                m.availability_score for m in materials) / len(materials)
            material_factor = avg_availability
        else:
            material_factor = 0.8

        labor_factor = 1.0 - (labor.hours - 4) * 0.02
        labor_factor = max(0.5, labor_factor)

        task_confidence = base_confidence * 0.5 + \
            material_factor * 0.3 + labor_factor * 0.2

        return max(0.0, min(1.0, task_confidence))

    def _prepare_confidence_data(self, analysis: TranscriptAnalysis,
                                 tasks: List[Task], project_context: Dict) -> Dict:
        return {
            "transcript_clarity": analysis.clarity_score,
            "room_dimensions": analysis.room_size > 0,
            "task_clarity_score": 0.8 if analysis.tasks_identified else 0.5,
            "material_specificity": 0.7,
            "has_budget_info": analysis.budget_preference != "moderate",
            "has_timeline": False,
            "materials_list": [
                {
                    "availability_score": material.availability_score,
                    "price_stability": 0.8,
                    "supplier_reliability": 0.85
                }
                for task in tasks for material in task.materials
            ],
            "task_standardization_score": 0.8,
            "complexity_accuracy": 0.75,
            "has_local_labor_rates": True,
            "skill_requirements_clarity": 0.8,
            "location": analysis.location,
            "complexity_level": self._determine_task_complexity("overall", analysis),
            "similar_projects_count": 0,
            "local_projects_count": 5,
            "data_recency_months": 3,
            "has_client_history": False
        }

    def _create_project_summary(self, analysis: TranscriptAnalysis) -> str:
        task_list = ", ".join(
            analysis.tasks_identified) if analysis.tasks_identified else "general renovation"
        return f"{analysis.room_size}sqm {analysis.room_type} renovation in {analysis.location}: {task_list}. Budget preference: {analysis.budget_preference}."

    def get_quote_summary(self, quote: Quote) -> Dict[str, any]:
        risk_assessment = self.confidence_scorer.assess_quote_risk(
            quote.dict())

        return {
            "quote_id": quote.quote_id,
            "total": quote.grand_total,
            "confidence": quote.global_confidence_score,
            "risk_level": risk_assessment["risk_level"],
            "task_count": sum(len(zone.tasks) for zone in quote.zones.values()),
            "location": quote.client_location,
            "recommendations": risk_assessment["recommended_action"]
        }
