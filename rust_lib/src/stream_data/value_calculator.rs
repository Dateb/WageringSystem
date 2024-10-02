use crate::stream_data::file_reading::deserialize::{RaceCard, Horse};

pub trait ValueCalculator: Send + Sync {
    fn calculate(&self, race_card: &RaceCard, horse: &Horse) -> f64;
}

#[derive(Clone)]
pub struct AgeCalculator;
impl ValueCalculator for AgeCalculator {
    fn calculate(&self, _race_card: &RaceCard, horse: &Horse) -> f64 {
        horse.age as f64
    }
}
