from dataclasses import dataclass

from ModelTuning.RankerConfigMCTS.EstimatorConfiguration import EstimatorConfiguration


@dataclass
class BetModelConfigurationNode:

    identifier: str
    max_score: float
    n_visits: int
    ranker_config: EstimatorConfiguration
