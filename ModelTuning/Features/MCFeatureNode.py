from dataclasses import dataclass
from typing import List


@dataclass
class MCFeatureNode:

    identifier: str
    max_score: float
    n_visits: int
    state: List[int]
