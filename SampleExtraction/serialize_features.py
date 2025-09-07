import pickle

from SampleExtraction.feature_sources.feature_sources import PreviousSource, MaxSource, MinSource, \
  SimpleAverageSource, SumSource, StreakSource, EMASource, DiffPreviousSource, DiffAverageSource, EMATimeSource
from SampleExtraction.feature_sources.value_calculators import WinProbabilityCalculator, HasWonCalculator, \
  MomentumCalculator, PlacePercentileCalculator, CompetitorsBeatenCalculator, RelativeDistanceBehindCalculator, \
  PurseCalculator, RatingCalculator, RaceClassCalculator, RaceGoingCalculator, \
  NumDaysCalculator, WeightCalculator, OneConstantCalculator, HasPlacedCalculator, AdjustedRaceDistanceCalculator

has_won_calculator = HasWonCalculator()
has_placed_calculator = HasPlacedCalculator()
momentum_calculator = MomentumCalculator()
win_probability_calculator = WinProbabilityCalculator()
place_percentile_calculator = PlacePercentileCalculator()
competitors_beaten_calculator = CompetitorsBeatenCalculator()
relative_distance_behind_calculator = RelativeDistanceBehindCalculator()
purse_calculator = PurseCalculator()
rating_calculator = RatingCalculator()
adjusted_race_distance_calculator = AdjustedRaceDistanceCalculator()
race_class_calculator = RaceClassCalculator()
race_going_calculator = RaceGoingCalculator()
num_days_calculator = NumDaysCalculator()
weight_calculator = WeightCalculator()
one_constant_calculator = OneConstantCalculator()

average_source_features = {
  win_probability_calculator: [
    [["breeder"], []],
    [["dam", "age"], []],
    [["jockey_id"], []],
    [["jockey_id"], ["estimated_going"]],
    [["jockey_id"], ["race_class"]],
    [["jockey_id"], ["race_type"]],
    [["jockey_id"], ["surface"]],
    [["jockey_id"], ["track_name"]],
    [["owner"], []],
    [["owner"], ["race_type"]],
    [["owner"], ["track_name"]],
    [["sire", "age"], []],
    [["subject_id"], []],
    [["subject_id"], ["category"]],
    [["subject_id"], ["race_class"]],
    [["subject_id"], ["race_type"]],
    [["trainer_id"], ["estimated_going"]],
    [["trainer_id"], ["race_class"]],
    [["trainer_id"], ["race_type"]],
    [["trainer_id"], ["surface"]],
    [["trainer_id"], ["track_name"]],
    [["jockey_id", "trainer_id"], []],
    [["subject_id", "jockey_id"], []],
    [["subject_id", "owner"], []],
    [["subject_id", "trainer_id"], []],
  ],
  has_won_calculator: [
    [["subject_id"], []],
    [["subject_id"], ["race_type"]],
  ],
  momentum_calculator: [
    [["jockey_id"], ["race_class"]],
    [["dam", "age"], []],
    [["owner"], []],
    [["subject_id"], []],
    [["subject_id"], ["race_class"]],
    [["trainer_id"], ["race_class"]],
    [["jockey_id", "trainer_id"], []],
    [["subject_id", "jockey_id"], []],
    [["subject_id", "owner"], []],
    [["subject_id", "trainer_id"], []],
  ],
  competitors_beaten_calculator: [
    [["breeder"], []],
    [["dam", "age"], []],
    [["jockey_id"], ["estimated_going"]],
    [["jockey_id"], ["race_class"]],
    [["jockey_id"], ["race_type"]],
    [["owner"], ["race_type"]],
    [["subject_id"], ["category"]],
    [["subject_id"], ["race_class"]],
    [["trainer_id"], ["estimated_going"]],
    [["trainer_id"], ["race_class"]],
    [["trainer_id"], ["race_type"]],
    [["jockey_id", "trainer_id"], []],
    [["subject_id", "jockey_id"], []],
    [["subject_id", "trainer_id"], []],
  ],
  relative_distance_behind_calculator: [
    [["jockey_id"], ["race_type"]],
    [["owner"], ["race_type"]],
    [["subject_id"], ["race_class"]],
    [["subject_id"], ["race_type"]],
    [["trainer_id"], ["race_type"]],
    [["jockey_id", "trainer_id"], []],
    [["subject_id", "jockey_id"], []],
    [["subject_id", "owner"], []],
    [["subject_id", "trainer_id"], []],
  ]
}

features = {
  EMATimeSource(window_size=0.1): average_source_features,
  EMATimeSource(window_size=0.01): average_source_features,
  EMATimeSource(window_size=0.001): average_source_features,
  PreviousSource():
  {
    win_probability_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["category"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]],
    ],
    has_placed_calculator: [
      [["subject_id"], []],
    ],
    momentum_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["track_name"]],
    ],
    competitors_beaten_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["category"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]],
    ],
    relative_distance_behind_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]],
    ],
    race_class_calculator: [
      [["subject_id"], []],
    ],
    adjusted_race_distance_calculator: [
      [["subject_id"], []]
    ]
  },
  SumSource(): {
    one_constant_calculator: [
      [["jockey_id"], []],
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["trainer_id"], []],
    ],
    purse_calculator: [
      [["jockey_id"], []],
      [["subject_id"], []],
      [["trainer_id"], []],
    ]
  },
  StreakSource(): {
    has_won_calculator: [
      [["subject_id"], []]
    ],
    has_placed_calculator: [
      [["subject_id"], []]
    ]
  },
  MaxSource(): {
    win_probability_calculator: [
      [["dam", "age"], []],
      [["jockey_id"], []],
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["trainer_id"], []],
    ],
    momentum_calculator: [
      [["dam", "age"], []],
      [["jockey_id"], []],
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]],
      [["trainer_id"], []],
    ],
    competitors_beaten_calculator: [
      [["dam", "age"], []],
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
    ],
    adjusted_race_distance_calculator: [
      [["subject_id"], []]
    ],
    weight_calculator: [
      [["subject_id"], []]
    ],
    purse_calculator: [
      [["jockey_id"], []],
      [["subject_id"], []],
      [["trainer_id"], []],
    ]
  },
  MinSource(): {
    adjusted_race_distance_calculator: [
      [["subject_id"], []]
    ],
    weight_calculator: [
      [["subject_id"], []]
    ]
  },
  DiffPreviousSource(): {
    num_days_calculator: [
      [["subject_id"], []], 
      [["subject_id", "jockey_id"], []], 
      [["subject_id"], ["race_class"]], 
      [["subject_id"], ["surface"]], 
      [["subject_id"], ["track_name"]]
    ],
  },
}

with open('features.pkl', 'wb') as f:
    pickle.dump(features, f)

print("Data serialized to features.pkl")