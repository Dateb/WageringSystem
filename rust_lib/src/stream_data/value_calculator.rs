use crate::stream_data::file_reading::deserialize::{RaceCard, Horse};

pub trait ValueCalculator: Send + Sync {
    fn calculate(&self, race_card: &RaceCard, horse: &Horse) -> Option<f64>;
    fn name(&self) -> &str;
}

#[derive(Clone)]
pub struct AgeCalculator;

impl ValueCalculator for AgeCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        Some(horse.age as f64)
    }
    fn name(&self) -> &str {
        "age"
    }
}

#[derive(Clone)]
pub struct WeightCalculator;

impl ValueCalculator for WeightCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        Some(horse.weight)
    }
    fn name(&self) -> &str {
        "weight"
    }
}

#[derive(Clone)]
pub struct WinProbabilityCalculator;

impl ValueCalculator for WinProbabilityCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        Some(horse.win_probability)
    }
    fn name(&self) -> &str {
        "win_probability"
    }
}

#[derive(Clone)]
pub struct PlacePercentileCalculator;

impl ValueCalculator for PlacePercentileCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        horse.place_percentile
    }
    fn name(&self) -> &str {
        "place_percentile"
    }
}

#[derive(Clone)]
pub struct RelativeDistanceBehindCalculator;

impl ValueCalculator for RelativeDistanceBehindCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        horse.relative_distance_behind
    }
    fn name(&self) -> &str {
        "relative_distance_behind"
    }
}

#[derive(Clone)]
pub struct PurseCalculator;

impl ValueCalculator for PurseCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        Some(horse.purse as f64)
    }
    fn name(&self) -> &str { "purse" }
}