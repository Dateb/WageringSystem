from dataclasses import dataclass

from ModelTuning.RankerConfigMCTS.RankerConfig import RankerConfig


@dataclass
class RankerConfigNode:

    identifier: str
    max_score: float
    n_visits: int
    ranker_config: RankerConfig
