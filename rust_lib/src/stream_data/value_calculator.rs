use chrono::{Datelike, NaiveDateTime};
use pyo3::{PyObject, Python, ToPyObject};
use pyo3::types::{PyFloat, PyString};
use crate::stream_data::file_reading::deserialize::{RaceCard, Horse};

#[derive(Clone)]
pub enum FeatureValue {
    Number(f64),
    Text(String),
    None,
}

impl FeatureValue {

    pub fn add(&self, other: &FeatureValue) -> FeatureValue {
        match (self, other) {
            (FeatureValue::Number(val1), FeatureValue::Number(val2)) => {
                FeatureValue::Number(val1 + val2)
            }
            _ => FeatureValue::None,
        }
    }

    pub fn subtract(&self, other: &FeatureValue) -> FeatureValue {
        match (self, other) {
            (FeatureValue::Number(val1), FeatureValue::Number(val2)) => {
                FeatureValue::Number(val1 - val2)
            }
            _ => FeatureValue::None,
        }
    }
}

impl ToPyObject for FeatureValue {
    fn to_object(&self, py: Python) -> PyObject {
        match self {
            FeatureValue::Number(val) => PyFloat::new(py, *val).to_object(py),
            FeatureValue::Text(val) => PyString::new(py, val).to_object(py),
            FeatureValue::None => py.None(),
        }
    }
}


pub trait ValueCalculator: Send + Sync {
    fn calculate(&self, race_card: &RaceCard, horse: &Horse) -> FeatureValue;
    fn name(&self) -> &str;
    fn is_categorical(&self) -> bool;
}

#[derive(Clone)]
pub struct OneCalculator;

impl ValueCalculator for OneCalculator {
    fn calculate(&self, _: &RaceCard, _: &Horse) -> FeatureValue {
        FeatureValue::Number(1.0)
    }
    fn name(&self) -> &str {
        "one"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct DistanceCalculator;

impl ValueCalculator for DistanceCalculator {
    fn calculate(&self, race_card: &RaceCard, _: &Horse) -> FeatureValue {
        FeatureValue::Number(race_card.distance as f64)
    }
    fn name(&self) -> &str {
        "distance"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct RaceClassCalculator;

impl ValueCalculator for RaceClassCalculator {
    fn calculate(&self, race_card: &RaceCard, _: &Horse) -> FeatureValue {
        let race_class_value = race_card.race_class.parse::<f64>();
        match race_class_value {
            Ok(value) => FeatureValue::Number(value),
            Err(_) => FeatureValue::None
        }
    }
    fn name(&self) -> &str {
        "race_class(value)"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct RaceDayCalculator;

impl ValueCalculator for RaceDayCalculator {
    fn calculate(&self, race_card: &RaceCard, _: &Horse) -> FeatureValue {
        let datetime =
            NaiveDateTime::parse_from_str(&race_card.date_time, "%Y-%m-%d %H:%M:%S")
                .expect("Failed to parse date");
        FeatureValue::Number(datetime.num_days_from_ce() as f64)
    }
    fn name(&self) -> &str { "race_day" }
    fn is_categorical(&self) -> bool { false }
}



#[derive(Clone)]
pub struct AgeCalculator;

impl ValueCalculator for AgeCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        FeatureValue::Number(horse.age as f64)
    }
    fn name(&self) -> &str {
        "age"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct WeightCalculator;

impl ValueCalculator for WeightCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        FeatureValue::Number(horse.weight)
    }
    fn name(&self) -> &str {
        "weight"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct MomentumCalculator;

impl ValueCalculator for MomentumCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match horse.momentum {
            Some(v) => FeatureValue::Number(v),
            _ => FeatureValue::None
        }
    }
    fn name(&self) -> &str {
        "momentum"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct HasWonCalculator;

impl ValueCalculator for HasWonCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match horse.has_won {
            Some(v) => FeatureValue::Number(v),
            _ => FeatureValue::None
        }
    }
    fn name(&self) -> &str {
        "has_won"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct HasPlacedCalculator;

impl ValueCalculator for HasPlacedCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match horse.has_placed {
            Some(v) => FeatureValue::Number(v),
            _ => FeatureValue::None
        }
    }
    fn name(&self) -> &str {
        "has_placed"
    }
    fn is_categorical(&self) -> bool { false }
}


#[derive(Clone)]
pub struct WinProbabilityCalculator;

impl ValueCalculator for WinProbabilityCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match horse.win_probability {
            Some(v) => FeatureValue::Number(v),
            _ => FeatureValue::None
        }
    }
    fn name(&self) -> &str {
        "win_probability"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct PlacePercentileCalculator;

impl ValueCalculator for PlacePercentileCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match horse.place_percentile {
            Some(v) => FeatureValue::Number(v),
            _ => FeatureValue::None
        }
    }
    fn name(&self) -> &str {
        "place_percentile"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct CompetitorsBeatenProbabilityCalculator;

impl ValueCalculator for CompetitorsBeatenProbabilityCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match horse.competitors_beaten_probability {
            Some(v) => FeatureValue::Number(v),
            _ => FeatureValue::None
        }
    }
    fn name(&self) -> &str {
        "competitors_beaten_probability"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct RelativeDistanceBehindCalculator;

impl ValueCalculator for RelativeDistanceBehindCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match horse.relative_distance_behind {
            Some(v) => FeatureValue::Number(v),
            _ => FeatureValue::None
        }
    }
    fn name(&self) -> &str {
        "relative_distance_behind"
    }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct PurseCalculator;

impl ValueCalculator for PurseCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        FeatureValue::Number(horse.purse as f64)
    }
    fn name(&self) -> &str { "purse" }
    fn is_categorical(&self) -> bool { false }
}

#[derive(Clone)]
pub struct GenderCalculator;

impl ValueCalculator for GenderCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match &horse.gender {
            Some(v) => FeatureValue::Text(v.clone()),
            None => FeatureValue::None
        }
    }
    fn name(&self) -> &str { "gender" }
    fn is_categorical(&self) -> bool { true }
}


#[derive(Clone)]
pub struct OriginCalculator;

impl ValueCalculator for OriginCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match &horse.origin {
            Some(v) => FeatureValue::Text(v.clone()),
            None => FeatureValue::None
        }
    }
    fn name(&self) -> &str { "origin" }
    fn is_categorical(&self) -> bool { true }
}

#[derive(Clone)]
pub struct RatingCalculator;

impl ValueCalculator for RatingCalculator {
    fn calculate(&self, _: &RaceCard, horse: &Horse) -> FeatureValue {
        match horse.rating {
            Some(v) => FeatureValue::Number(v),
            _ => FeatureValue::None
        }
    }
    fn name(&self) -> &str {
        "rating"
    }
    fn is_categorical(&self) -> bool { false }
}
