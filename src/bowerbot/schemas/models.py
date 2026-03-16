"""Data schemas used across BowerBot."""

from enum import Enum

from pydantic import BaseModel, Field


# ── Asset Schemas ──────────────────────────────────────────────


class AssetFormat(str, Enum):
    """Supported 3D asset formats."""

    USD = "usd"
    USDA = "usda"
    USDC = "usdc"
    USDZ = "usdz"


class AssetMetadata(BaseModel):
    """Metadata for a 3D asset sourced from any skill."""

    name: str
    source_skill: str  # e.g. "sketchfab", "local", "cgtrader"
    source_id: str  # Skill-specific identifier (URL, SKU, file path)
    file_path: str | None = None  # Local path after download
    format: AssetFormat = AssetFormat.USDZ
    bbox_min: tuple[float, float, float] | None = None
    bbox_max: tuple[float, float, float] | None = None
    tags: list[str] = Field(default_factory=list)
    license: str | None = None


# ── Scene Graph Schemas ────────────────────────────────────────


class PlacementCategory(str, Enum):
    """Where an object category gets placed by default."""

    FLOOR = "floor"  # Y = 0 (tables, chairs, shelves)
    SURFACE = "surface"  # Y = furniture_height (products, displays)
    CEILING = "ceiling"  # Y = room_height (pendant lights)
    WALL = "wall"  # Against wall boundary


class SceneObject(BaseModel):
    """An object placed in the scene graph."""

    prim_path: str  # e.g. "/Scene/Furniture/Table_01"
    asset: AssetMetadata
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotate: tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    category: PlacementCategory = PlacementCategory.FLOOR


# ── Validation Schemas ─────────────────────────────────────────


class Severity(str, Enum):
    """Validation issue severity."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(BaseModel):
    """A single validation finding."""

    severity: Severity
    message: str
    prim_path: str | None = None


class ValidationResult(BaseModel):
    """Result of running the validator on a stage."""

    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)
