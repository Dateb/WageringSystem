use crate::stream_data::file_reading::deserialize::{RaceCard, Horse};

pub trait ValueCalculator: Send + Sync {
    fn calculate(&self, race_card: &RaceCard, horse: &Horse) -> f64;
    fn name(&self) -> &str;
}

#[derive(Clone)]
pub struct AgeCalculator;

impl ValueCalculator for AgeCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> f64 {
        horse.age as f64
    }
    fn name(&self) -> &str {
        "age"
    }
}

#[derive(Clone)]
pub struct WeightCalculator;

impl ValueCalculator for WeightCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> f64 {
        horse.weight
    }
    fn name(&self) -> &str {
        "weight"
    }
}

#[derive(Clone)]
pub struct WinProbabilityCalculator;

impl ValueCalculator for WinProbabilityCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> f64 {
        let mut win_probability = -1.0;
        if horse.sp >= 1.0 {
            win_probability = 1.0 / horse.sp
        }

        win_probability
    }
    fn name(&self) -> &str {
        "win_probability"
    }
}
