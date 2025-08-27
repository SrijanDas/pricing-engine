from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import uuid


class TaskType(str, Enum):
    DEMOLITION = "demolition"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    TILING = "tiling"
    PAINTING = "painting"
    FLOORING = "flooring"
    FIXTURES = "fixtures"
    WATERPROOFING = "waterproofing"


class MaterialCategory(str, Enum):
    TILES = "tiles"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    PAINT = "paint"
    FIXTURES = "fixtures"
    TOOLS = "tools"
    CONSUMABLES = "consumables"


class VATRate(str, Enum):
    STANDARD = "standard"  # 20%
    REDUCED = "reduced"    # 10%
    ZERO = "zero"         # 0%


class Material(BaseModel):
    name: str
    category: MaterialCategory
    quantity: float
    unit: str  # sqm, pieces, kg, etc.
    unit_price: float
    total: float
    supplier: Optional[str] = None
    availability_score: float = Field(default=1.0, ge=0.0, le=1.0)


class Labor(BaseModel):
    hours: float
    rate: float  # per hour
    total: float
    skill_level: str = "skilled"  # skilled, semi-skilled, unskilled
    workers_needed: int = 1


class Task(BaseModel):
    name: str
    task_type: TaskType
    description: str
    labor: Labor
    materials: List[Material]
    estimated_duration: str
    vat_rate: float
    vat_percentage: str
    subtotal: float
    vat_amount: float
    total_price: float
    margin: float = Field(ge=0.15, description="Minimum 15% margin")
    confidence_score: float = Field(ge=0.0, le=1.0)
    complexity_factor: float = Field(default=1.0, ge=0.5, le=2.0)


class Zone(BaseModel):
    name: str
    area: float  # sqm
    tasks: List[Task]
    zone_total: float
    zone_confidence: float = Field(ge=0.0, le=1.0)


class Quote(BaseModel):
    quote_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    client_location: str
    project_summary: str
    zones: Dict[str, Zone]
    global_confidence_score: float = Field(ge=0.0, le=1.0)
    total_before_vat: float
    total_vat: float
    grand_total: float


class TranscriptAnalysis(BaseModel):
    location: str
    room_type: str
    room_size: float
    tasks_identified: List[str]
    budget_preference: str  # budget-conscious, mid-range, premium
    special_requirements: List[str] = Field(default_factory=list)
    clarity_score: float = Field(ge=0.0, le=1.0)
    raw_transcript: str


class FeedbackData(BaseModel):
    quote_id: str
    accepted: bool
    feedback_reason: str
    suggested_price: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
