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

#[derive(Clone)]
pub struct JockeyIdCategory;

impl CategoryCalculator for JockeyIdCategory {
    fn get_category(&self, race_card: &RaceCard, horse: &Horse) -> String {
        horse.jockey_id.to_string()
    }
    fn name(&self) -> &str { "jockey_id" }
}

#[derive(Clone)]
pub struct TrainerIdCategory;

impl CategoryCalculator for TrainerIdCategory {
    fn get_category(&self, race_card: &RaceCard, horse: &Horse) -> String {
        horse.trainer_id.to_string()
    }
    fn name(&self) -> &str { "trainer_id" }
}

#[derive(Clone)]
pub struct OwnerIdCategory;

impl CategoryCalculator for OwnerIdCategory {
    fn get_category(&self, race_card: &RaceCard, horse: &Horse) -> String {
        horse.owner_id.to_string()
    }
    fn name(&self) -> &str { "owner_id" }
}

#[derive(Clone)]
pub struct BreederIdCategory;

impl CategoryCalculator for BreederIdCategory {
    fn get_category(&self, race_card: &RaceCard, horse: &Horse) -> String {
        horse.breeder_id.to_string()
    }
    fn name(&self) -> &str { "breeder_id" }
}


#[derive(Clone)]
pub struct RaceTypeCategory;

impl CategoryCalculator for RaceTypeCategory {
    fn get_category(&self, race_card: &RaceCard, horse: &Horse) -> String {
        race_card.race_type.to_string()
    }
    fn name(&self) -> &str {
        "race_type"
    }
}

#[derive(Clone)]
pub struct RaceClassCategory;

impl CategoryCalculator for RaceClassCategory {
    fn get_category(&self, race_card: &RaceCard, horse: &Horse) -> String {
        race_card.race_class.to_string()
    }
    fn name(&self) -> &str {
        "race_class"
    }
}