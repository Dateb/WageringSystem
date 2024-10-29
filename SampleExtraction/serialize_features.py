import pickle

from sktime.distances import distance

from SampleExtraction.feature_sources.feature_sources import PreviousSource, MaxSource, MinSource, \
  SimpleAverageSource, SumSource, StreakSource, EMASource, DiffPreviousSource, DiffAverageSource
from SampleExtraction.feature_sources.value_calculators import WinProbabilityCalculator, HasWonCalculator, \
  MomentumCalculator, PlacePercentileCalculator, CompetitorsBeatenCalculator, RelativeDistanceBehindCalculator, \
  PurseCalculator, RatingCalculator, RaceDistanceCalculator, RaceClassCalculator, RaceGoingCalculator, \
  NumDaysCalculator, WeightCalculator, OneConstantCalculator

has_won_calculator = HasWonCalculator()
momentum_calculator = MomentumCalculator()
win_probability_calculator = WinProbabilityCalculator()
place_percentile_calculator = PlacePercentileCalculator()
competitors_beaten_calculator = CompetitorsBeatenCalculator()
relative_distance_behind_calculator = RelativeDistanceBehindCalculator()
purse_calculator = PurseCalculator()
rating_calculator = RatingCalculator()
race_distance_calculator = RaceDistanceCalculator()
race_class_calculator = RaceClassCalculator()
race_going_calculator = RaceGoingCalculator()
num_days_calculator = NumDaysCalculator()
weight_calculator = WeightCalculator()
one_constant_calculator = OneConstantCalculator()

features = {
  SimpleAverageSource(): 
  {
    has_won_calculator: [
      [["jockey_id"], ["race_class"]],
      [["trainer_id"], ["race_class"]],
    ],
    momentum_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["surface"]]
    ],
    win_probability_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]]
    ],
    place_percentile_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]]
    ],
    competitors_beaten_calculator: [
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["race_class"]]
    ],
    relative_distance_behind_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]]
    ],
    purse_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]]
    ]
  },
  EMASource():
  {
    has_won_calculator: [
      [["jockey_id"], []],
      [["trainer_id"], []]
    ],
    momentum_calculator: [
      [["jockey_id"], []],
      [["trainer_id"], []]
    ],
    win_probability_calculator: [
      [["jockey_id"], []],
      [["trainer_id"], []]
    ],
    place_percentile_calculator: [
      [["jockey_id"], []],
      [["trainer_id"], []]
    ],
    competitors_beaten_calculator: [
      [["jockey_id"], []],
      [["trainer_id"], []]
    ],
    relative_distance_behind_calculator: [
      [["jockey_id"], []],
      [["trainer_id"], []]
    ],
    purse_calculator: [
      [["jockey_id"], []],
      [["trainer_id"], []]
    ]
  },
  PreviousSource():
  {
    win_probability_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]]
    ],
    rating_calculator: [
      [["subject_id"], []],
    ],
    relative_distance_behind_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]]
    ]
  },
  DiffPreviousSource(): {
    race_distance_calculator: [
      [["subject_id"], []]
    ],
    race_going_calculator: [
      [["subject_id"], []]
    ],
    num_days_calculator: [
      [["subject_id"], []], 
      [["subject_id", "jockey_id"], []], 
      [["subject_id"], ["race_class"]], 
      [["subject_id"], ["surface"]], 
      [["subject_id"], ["track_name"]]
    ],
    race_class_calculator: [
      [["subject_id"], []], 
      [["subject_id"], ["surface"]], 
      [["subject_id", "trainer_id"], []]
    ]
  },
  DiffAverageSource(): {
    race_distance_calculator: [
      [["subject_id"], []]
    ],
    race_going_calculator: [
      [["subject_id"], []]
    ],
    race_class_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]],
      [["jockey_id"], []],
      [["trainer_id"], []],
      [["trainer_id"], ["surface"]],
      [["trainer_id"], ["track_name"]],
      [["subject_id", "jockey_id"], []],
      [["subject_id", "trainer_id"], []]
    ],
    weight_calculator: [
      [["subject_id"], []]
    ]
  },
  MaxSource(): {
    win_probability_calculator: [
      [["subject_id"], []]
    ],
    momentum_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]]
    ],
    place_percentile_calculator: [
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["surface"]]
    ],
    relative_distance_behind_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["surface"]]
    ],
    purse_calculator: [
      [["subject_id"], []],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["surface"]]
    ]
  },
  SumSource(): {
    one_constant_calculator: [
      [["subject_id"], []],
      [["jockey_id"], []],
      [["trainer_id"], []],
    ],
  },
}

with open('features.pkl', 'wb') as f:
    pickle.dump(features, f)

print("Data serialized to features.pkl")