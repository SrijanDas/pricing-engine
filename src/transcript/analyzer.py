import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from src.models import TranscriptAnalysis
import re


class TranscriptAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.model = "gpt-4o-mini"

    def analyze_transcript(self, transcript: str) -> TranscriptAnalysis:
        try:
            system_prompt = self._get_system_prompt()
            user_prompt = self._get_user_prompt(transcript)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            analysis_text = response.choices[0].message.content
            analysis_data = self._parse_analysis_response(analysis_text)

            return TranscriptAnalysis(
                location=analysis_data.get("location", "Unknown"),
                room_type=analysis_data.get("room_type", "bathroom"),
                room_size=analysis_data.get("room_size", 4.0),
                tasks_identified=analysis_data.get("tasks_identified", []),
                budget_preference=analysis_data.get(
                    "budget_preference", "moderate"),
                special_requirements=analysis_data.get(
                    "special_requirements", []),
                clarity_score=analysis_data.get("clarity_score", 0.7),
                raw_transcript=transcript
            )

        except Exception as e:
            return self._get_fallback_analysis(transcript)

    def _get_system_prompt(self) -> str:
        return """
You are an expert renovation analyst for Donizo, a French renovation company. 
Your job is to analyze voice transcripts from clients describing their renovation needs and extract structured information.

You must respond with a JSON object containing these fields:
- location: The city/location mentioned (or "Unknown" if not specified)
- room_type: Type of room being renovated (bathroom, kitchen, etc.)
- room_size: Estimated size in square meters (extract or estimate based on description)
- tasks_identified: List of renovation tasks mentioned (e.g. ["remove tiles", "plumbing work", "install vanity"])
- budget_preference: Client's budget preference ("budget-conscious", "moderate", "premium", "luxury")
- special_requirements: Any special needs or constraints mentioned
- clarity_score: Score from 0.0 to 1.0 indicating how clear and complete the transcript is

Guidelines:
- Extract explicit information first
- Make reasonable inferences where information is missing
- Use standard renovation terminology
        # Room size patterns
        - For room sizes, typical French bathroom sizes are 2-6sqm
- Budget preferences can be inferred from language like "budget-conscious", "quality materials", etc.
- Common bathroom tasks: demolition, plumbing, electrical, tiling, painting, fixture installation
- Be conservative with inferences - if unsure, use default values

Respond only with valid JSON.
"""

    def _get_user_prompt(self, transcript: str) -> str:
        return f"""
Please analyze this renovation transcript and extract the information as JSON:

Transcript: "{transcript}"

Remember to respond with valid JSON only.
"""

    def _parse_analysis_response(self, response_text: str) -> Dict:
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                return json.loads(response_text)

        except json.JSONDecodeError:
            return self._get_default_analysis_data()

    def _get_default_analysis_data(self) -> Dict:
        return {
            "location": "Unknown",
            "room_type": "bathroom",
            "room_size": 4.0,
            "tasks_identified": ["renovation"],
            "budget_preference": "moderate",
            "special_requirements": [],
            "clarity_score": 0.5
        }

    def _get_fallback_analysis(self, transcript: str) -> TranscriptAnalysis:
        transcript_lower = transcript.lower()

        location = self._extract_location_fallback(transcript_lower)

        room_size = self._extract_room_size_fallback(transcript_lower)

        tasks = self._extract_tasks_fallback(transcript_lower)

        budget = self._extract_budget_fallback(transcript_lower)

        clarity_score = min(
            1.0, len(transcript.split()) / 20)

        return TranscriptAnalysis(
            location=location,
            room_type="bathroom",
            room_size=room_size,
            tasks_identified=tasks,
            budget_preference=budget,
            special_requirements=[],
            clarity_score=clarity_score,
            raw_transcript=transcript
        )

    def _extract_location_fallback(self, transcript: str) -> str:
        french_cities = [
            "paris", "marseille", "lyon", "toulouse", "nice", "nantes",
            "strasbourg", "montpellier", "bordeaux", "lille", "rennes"
        ]

        for city in french_cities:
            if city in transcript:
                return city.title()

        return "Unknown"

    def _extract_room_size_fallback(self, transcript: str) -> float:
        size_patterns = [
            r'(\d+(?:\.\d+)?)\s*m[²2]',
            r'(\d+(?:\.\d+)?)\s*sqm',
            r'(\d+(?:\.\d+)?)\s*square\s*meters?',
            r'(\d+(?:\.\d+)?)\s*metres?\s*carr[ée]s?'
        ]

        for pattern in size_patterns:
            match = re.search(pattern, transcript)
            if match:
                return float(match.group(1))

        if any(word in transcript for word in ["small", "petite", "tiny"]):
            return 3.0
        elif any(word in transcript for word in ["large", "grande", "big"]):
            return 8.0
        else:
            return 4.0  # Average bathroom size

    def _extract_tasks_fallback(self, transcript: str) -> List[str]:
        task_keywords = {
            "remove tiles": ["remove tiles", "tile removal", "enlever carrelage"],
            "plumbing": ["plumbing", "plomberie", "pipes", "shower", "toilet"],
            "electrical": ["electrical", "électricité", "wiring", "lights"],
            "tiling": ["tiles", "tiling", "carrelage", "lay tiles"],
            "painting": ["paint", "painting", "peinture", "repaint"],
            "install fixtures": ["vanity", "toilet", "fixtures", "install"]
        }

        identified_tasks = []

        for task, keywords in task_keywords.items():
            if any(keyword in transcript for keyword in keywords):
                identified_tasks.append(task)

        return identified_tasks if identified_tasks else ["renovation"]

    def _extract_budget_fallback(self, transcript: str) -> str:
        budget_keywords = {
            "budget-conscious": ["budget", "cheap", "économique", "pas cher", "cost-effective"],
            "premium": ["quality", "high-end", "premium", "qualité", "haut de gamme"],
            "luxury": ["luxury", "luxe", "designer", "custom", "sur mesure"]
        }

        for budget_level, keywords in budget_keywords.items():
            if any(keyword in transcript for keyword in keywords):
                return budget_level

        return "moderate"  # Default

    def analyze_batch(self, transcripts: List[str]) -> List[TranscriptAnalysis]:
        results = []

        for transcript in transcripts:
            analysis = self.analyze_transcript(transcript)
            results.append(analysis)

        return results

    def get_analysis_summary(self, analysis: TranscriptAnalysis) -> Dict[str, any]:
        return {
            "extraction_quality": "Good" if analysis.clarity_score > 0.7 else "Needs Review",
            "location_confidence": "High" if analysis.location != "Unknown" else "Low",
            "task_count": len(analysis.tasks_identified),
            "estimated_project_scope": self._estimate_project_scope(analysis),
            "data_completeness": self._assess_data_completeness(analysis)
        }

    def _estimate_project_scope(self, analysis: TranscriptAnalysis) -> str:
        task_count = len(analysis.tasks_identified)
        room_size = analysis.room_size

        if task_count >= 5 or room_size >= 8:
            return "Large renovation"
        elif task_count >= 3 or room_size >= 6:
            return "Medium renovation"
        else:
            return "Small renovation"

    def _assess_data_completeness(self, analysis: TranscriptAnalysis) -> Dict[str, bool]:
        return {
            "has_location": analysis.location != "Unknown",
            "has_dimensions": analysis.room_size > 0,
            "has_tasks": len(analysis.tasks_identified) > 0,
            "has_budget_info": analysis.budget_preference != "moderate",
            "has_special_requirements": len(analysis.special_requirements) > 0
        }
