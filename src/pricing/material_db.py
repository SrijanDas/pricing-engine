from typing import Dict, List, Optional
from src.models import Material, MaterialCategory


class MaterialDatabase:
    def __init__(self):
        self.materials = self._initialize_materials()

    def _initialize_materials(self) -> Dict[str, Dict]:
        return {
            # TILES
            "ceramic_floor_tiles": {
                "category": MaterialCategory.TILES,
                "base_price": 25.0,  # per sqm
                "unit": "sqm",
                "description": "Standard ceramic floor tiles",
                "supplier": "Leroy Merlin",
                "availability_score": 0.95,
                "variants": {
                    "basic": {"multiplier": 1.0, "price": 25.0},
                    "premium": {"multiplier": 1.8, "price": 45.0},
                    "luxury": {"multiplier": 3.0, "price": 75.0}
                }
            },
            "wall_tiles": {
                "category": MaterialCategory.TILES,
                "base_price": 30.0,  # per m2
                "unit": "sqm",
                "description": "Wall tiles for bathroom",
                "supplier": "Point P",
                "availability_score": 0.90,
                "variants": {
                    "basic": {"multiplier": 1.0, "price": 30.0},
                    "premium": {"multiplier": 1.5, "price": 45.0},
                    "luxury": {"multiplier": 2.5, "price": 75.0}
                }
            },
            "tile_adhesive": {
                "category": MaterialCategory.CONSUMABLES,
                "base_price": 15.0,  # per 25kg bag
                "unit": "25kg bag",
                "description": "Tile adhesive",
                "supplier": "Weber",
                "availability_score": 0.98,
                "coverage": 5.0  # sqm per bag
            },
            "grout": {
                "category": MaterialCategory.CONSUMABLES,
                "base_price": 12.0,  # per 5kg bag
                "unit": "5kg bag",
                "description": "Tile grout",
                "supplier": "Mapei",
                "availability_score": 0.95,
                "coverage": 10.0  # sqm per bag
            },

            # PLUMBING
            "toilet": {
                "category": MaterialCategory.PLUMBING,
                "base_price": 180.0,
                "unit": "piece",
                "description": "Standard toilet with cistern",
                "supplier": "Sanitaire Discount",
                "availability_score": 0.92,
                "variants": {
                    "basic": {"multiplier": 1.0, "price": 180.0},
                    "comfort": {"multiplier": 1.5, "price": 270.0},
                    "premium": {"multiplier": 2.2, "price": 400.0}
                }
            },
            "vanity_sink": {
                "category": MaterialCategory.FIXTURES,
                "base_price": 350.0,
                "unit": "piece",
                "description": "Bathroom vanity with sink",
                "supplier": "IKEA",
                "availability_score": 0.88,
                "variants": {
                    "basic": {"multiplier": 1.0, "price": 350.0},
                    "mid_range": {"multiplier": 1.4, "price": 490.0},
                    "premium": {"multiplier": 2.0, "price": 700.0}
                }
            },
            "shower_mixer": {
                "category": MaterialCategory.PLUMBING,
                "base_price": 120.0,
                "unit": "piece",
                "description": "Shower mixer tap",
                "supplier": "Grohe",
                "availability_score": 0.85,
                "variants": {
                    "basic": {"multiplier": 1.0, "price": 120.0},
                    "thermostatic": {"multiplier": 1.8, "price": 216.0},
                    "premium": {"multiplier": 2.5, "price": 300.0}
                }
            },
            "copper_pipes": {
                "category": MaterialCategory.PLUMBING,
                "base_price": 8.5,  # per meter
                "unit": "m",
                "description": "15mm copper pipes",
                "supplier": "Brico Dépôt",
                "availability_score": 0.95
            },
            "pvc_drain_pipe": {
                "category": MaterialCategory.PLUMBING,
                "base_price": 5.2,  # per meter
                "unit": "m",
                "description": "110mm PVC drain pipe",
                "supplier": "Brico Dépôt",
                "availability_score": 0.98
            },

            # ELECTRICAL
            "electrical_cable": {
                "category": MaterialCategory.ELECTRICAL,
                "base_price": 2.8,  # per meter
                "unit": "m",
                "description": "2.5mm² electrical cable",
                "supplier": "Rexel",
                "availability_score": 0.96
            },
            "bathroom_light_fixture": {
                "category": MaterialCategory.ELECTRICAL,
                "base_price": 45.0,
                "unit": "piece",
                "description": "IP44 bathroom light fixture",
                "supplier": "Castorama",
                "availability_score": 0.90,
                "variants": {
                    "basic": {"multiplier": 1.0, "price": 45.0},
                    "led": {"multiplier": 1.4, "price": 63.0},
                    "designer": {"multiplier": 2.5, "price": 112.0}
                }
            },

            # PAINT
            "bathroom_paint": {
                "category": MaterialCategory.PAINT,
                "base_price": 35.0,  # per 2.5L
                "unit": "2.5L",
                "description": "Humidity-resistant bathroom paint",
                "supplier": "Dulux Valentine",
                "availability_score": 0.93,
                "coverage": 25.0  # sqm per 2.5L
            },
            "primer": {
                "category": MaterialCategory.PAINT,
                "base_price": 25.0,  # per 2.5L
                "unit": "2.5L",
                "description": "Wall primer",
                "supplier": "Dulux Valentine",
                "availability_score": 0.95,
                "coverage": 30.0  # sqm per 2.5L
            },

            # CONSUMABLES
            "cement": {
                "category": MaterialCategory.CONSUMABLES,
                "base_price": 8.5,  # per 25kg bag
                "unit": "25kg bag",
                "description": "Portland cement",
                "supplier": "Lafarge",
                "availability_score": 0.99
            },
            "sand": {
                "category": MaterialCategory.CONSUMABLES,
                "base_price": 45.0,  # per tonne
                "unit": "tonne",
                "description": "Fine sand",
                "supplier": "Local supplier",
                "availability_score": 0.98
            },
            "waterproofing_membrane": {
                "category": MaterialCategory.CONSUMABLES,
                "base_price": 15.0,  # per sqm
                "unit": "sqm",
                "description": "Waterproofing membrane",
                "supplier": "Sika",
                "availability_score": 0.85
            }
        }

    def get_material_price(self, material_name: str, quantity: float,
                           variant: str = "basic") -> Material:
        if material_name not in self.materials:
            raise ValueError(
                f"Material '{material_name}' not found in database")

        material_data = self.materials[material_name]

        if "variants" in material_data and variant in material_data["variants"]:
            unit_price = material_data["variants"][variant]["price"]
        else:
            unit_price = material_data["base_price"]

        total = quantity * unit_price

        return Material(
            name=material_data["description"],
            category=material_data["category"],
            quantity=quantity,
            unit=material_data["unit"],
            unit_price=unit_price,
            total=total,
            supplier=material_data.get("supplier"),
            availability_score=material_data.get("availability_score", 1.0)
        )

    def estimate_coverage_needs(self, material_name: str, area: float) -> float:
        if material_name not in self.materials:
            return 0.0

        material_data = self.materials[material_name]

        # Coverage-based materials
        coverage_per_unit = material_data.get("coverage", 1.0)
        return max(1.0, area / coverage_per_unit)  # Minimum 1 unit

    def get_task_materials(self, task_type: str, area: float = 4.0,
                           budget_level: str = "basic") -> List[Material]:
        materials = []

        if task_type == "tiling":
            floor_tiles = self.get_material_price(
                "ceramic_floor_tiles", area, budget_level
            )
            materials.append(floor_tiles)

            wall_area = area * 3  # Rough estimate
            wall_tiles = self.get_material_price(
                "wall_tiles", wall_area, budget_level
            )
            materials.append(wall_tiles)

            adhesive_bags = self.estimate_coverage_needs(
                "tile_adhesive", area + wall_area)
            adhesive = self.get_material_price("tile_adhesive", adhesive_bags)
            materials.append(adhesive)

            grout_bags = self.estimate_coverage_needs(
                "grout", area + wall_area)
            grout = self.get_material_price("grout", grout_bags)
            materials.append(grout)

        elif task_type == "plumbing":
            toilet = self.get_material_price("toilet", 1, budget_level)
            materials.append(toilet)

            mixer = self.get_material_price("shower_mixer", 1, budget_level)
            materials.append(mixer)

            copper_pipes = self.get_material_price("copper_pipes", 10)
            materials.append(copper_pipes)

            drain_pipe = self.get_material_price("pvc_drain_pipe", 3)
            materials.append(drain_pipe)

        elif task_type == "painting":
            paint_area = area * 2.5  # Walls height estimate
            paint_liters = self.estimate_coverage_needs(
                "bathroom_paint", paint_area)
            paint = self.get_material_price("bathroom_paint", paint_liters)
            materials.append(paint)

            primer_liters = self.estimate_coverage_needs("primer", paint_area)
            primer = self.get_material_price("primer", primer_liters)
            materials.append(primer)

        elif task_type == "fixtures":
            vanity = self.get_material_price("vanity_sink", 1, budget_level)
            materials.append(vanity)

            light = self.get_material_price(
                "bathroom_light_fixture", 1, budget_level)
            materials.append(light)

        return materials

    def search_materials(self, category: Optional[MaterialCategory] = None,
                         max_price: Optional[float] = None) -> List[str]:
        results = []

        for name, data in self.materials.items():
            if category and data["category"] != category:
                continue
            if max_price and data["base_price"] > max_price:
                continue
            results.append(name)

        return results
