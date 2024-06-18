from dataclasses import dataclass
from typing import Optional


@dataclass
class PowerLogResult:
    timestamp: float
    draw: float
    misc: Optional[dict] = None
