use crate::stream_data::file_reading::deserialize::{RaceCard, Horse};

pub trait CategoryCalculator: Send + Sync {
    fn get_category(&self, race_card: &RaceCard, horse: &Horse) -> String;
    fn name(&self) -> &str;
}

#[derive(Clone)]
pub struct HorseIdCategory;

impl CategoryCalculator for HorseIdCategory {
    fn get_category(&self, race_card: &RaceCard, horse: &Horse) -> String {
        horse.id.to_string()
    }
    fn name(&self) -> &str {
        "horse_id"
    }
}
