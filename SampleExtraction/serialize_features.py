import pickle

from SampleExtraction.feature_sources.feature_sources import PreviousSource, MaxSource, MinSource, \
  AverageSource, SumSource, StreakSource
from SampleExtraction.feature_sources.value_calculators import win_probability, has_placed, competitors_beaten, \
  momentum, relative_distance_behind, race_class, adjusted_race_distance, weight, purse, has_won, one_constant

average_source_features = {
  win_probability: [
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
  has_won: [
    [["subject_id"], []],
    [["subject_id"], ["race_type"]],
  ],
  momentum: [
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
  competitors_beaten: [
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
  relative_distance_behind: [
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
  AverageSource(window_size=0.1): average_source_features,
  AverageSource(window_size=0.01): average_source_features,
  AverageSource(window_size=0.001): average_source_features,
  PreviousSource():
  {
    win_probability: [
      [["subject_id"], []],
      [["subject_id"], ["category"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]],
    ],
    has_placed: [
      [["subject_id"], []],
    ],
    momentum: [
      [["subject_id"], []],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["track_name"]],
    ],
    competitors_beaten: [
      [["subject_id"], []],
      [["subject_id"], ["category"]],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["race_type"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]],
    ],
    relative_distance_behind: [
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]],
    ],
    race_class: [
      [["subject_id"], []],
    ],
    adjusted_race_distance: [
      [["subject_id"], []]
    ]
  },
  SumSource(): {
    one_constant: [
      [["jockey_id"], []],
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["trainer_id"], []],
    ],
    purse: [
      [["jockey_id"], []],
      [["subject_id"], []],
      [["trainer_id"], []],
    ]
  },
  StreakSource(): {
    has_won: [
      [["subject_id"], []]
    ],
    has_placed: [
      [["subject_id"], []]
    ]
  },
  MaxSource(): {
    win_probability: [
      [["dam", "age"], []],
      [["jockey_id"], []],
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["trainer_id"], []],
    ],
    momentum: [
      [["dam", "age"], []],
      [["jockey_id"], []],
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
      [["subject_id"], ["track_name"]],
      [["trainer_id"], []],
    ],
    competitors_beaten: [
      [["dam", "age"], []],
      [["subject_id"], []],
      [["subject_id"], ["race_class"]],
      [["subject_id"], ["surface"]],
    ],
    adjusted_race_distance: [
      [["subject_id"], []]
    ],
    weight: [
      [["subject_id"], []]
    ],
    purse: [
      [["jockey_id"], []],
      [["subject_id"], []],
      [["trainer_id"], []],
    ]
  },
  MinSource(): {
    adjusted_race_distance: [
      [["subject_id"], []]
    ],
    weight: [
      [["subject_id"], []]
    ]
  }
}

with open('features.pkl', 'wb') as f:
    pickle.dump(features, f)

print("Data serialized to features.pkl")