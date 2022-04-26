from dataclasses import dataclass
from typing import List


@dataclass
class RaceHistory:
    subject_id: str
    race_ids: List[str]
