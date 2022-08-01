from dataclasses import dataclass

from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration


@dataclass
class BetModelConfigurationNode:

    identifier: str
    max_score: float
    n_visits: int
    ranker_config: BetModelConfiguration
