"""Configuration shared by the CLI, pipeline, and Streamlit app."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Sequence

DEFAULT_REGIONS: tuple[str, ...] = ("North", "Central", "South")
DEFAULT_START_DATE = "2015-01-01"
DEFAULT_END_DATE = "2024-12-31"
DEFAULT_RANDOM_SEED = 42


def _normalise_date(value: str | date | datetime) -> str:
    """Return a date-like value in the ISO ``YYYY-MM-DD`` format."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    # Parsing here gives the caller a useful error before data generation.
    return datetime.strptime(str(value), "%Y-%m-%d").date().isoformat()


@dataclass(frozen=True)
class AnalyzerConfig:
    """Runtime settings for a reproducible climate analysis."""

    start_date: str = DEFAULT_START_DATE
    end_date: str = DEFAULT_END_DATE
    regions: tuple[str, ...] = DEFAULT_REGIONS
    random_seed: int = DEFAULT_RANDOM_SEED
    output_dir: Path = Path("outputs")

    def __post_init__(self) -> None:
        start = _normalise_date(self.start_date)
        end = _normalise_date(self.end_date)
        regions = tuple(str(region).strip() for region in self.regions if str(region).strip())
        if not regions:
            raise ValueError("At least one region is required.")
        if date.fromisoformat(start) > date.fromisoformat(end):
            raise ValueError("start_date must be on or before end_date.")
        if len(set(regions)) != len(regions):
            raise ValueError("regions must not contain duplicates.")
        object.__setattr__(self, "start_date", start)
        object.__setattr__(self, "end_date", end)
        object.__setattr__(self, "regions", regions)
        object.__setattr__(self, "random_seed", int(self.random_seed))
        object.__setattr__(self, "output_dir", Path(self.output_dir))

    @property
    def start(self) -> date:
        """Parsed start date."""
        return date.fromisoformat(self.start_date)

    @property
    def end(self) -> date:
        """Parsed end date."""
        return date.fromisoformat(self.end_date)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation for reports."""
        return {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "regions": list(self.regions),
            "random_seed": self.random_seed,
            "output_dir": str(self.output_dir),
        }


def config_from_values(
    *,
    start_date: str = DEFAULT_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    regions: Sequence[str] = DEFAULT_REGIONS,
    random_seed: int = DEFAULT_RANDOM_SEED,
    output_dir: str | Path = Path("outputs"),
) -> AnalyzerConfig:
    """Build a validated configuration from CLI- or UI-friendly values."""
    return AnalyzerConfig(
        start_date=start_date,
        end_date=end_date,
        regions=tuple(regions),
        random_seed=random_seed,
        output_dir=Path(output_dir),
    )
