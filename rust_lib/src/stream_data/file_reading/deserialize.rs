use std::collections::HashMap;
use serde::Deserialize;

#[derive(Debug, Deserialize, PartialEq)]
pub struct Horse {
    pub id: u32,
    pub jockey_id: String,
    pub trainer_id: String,
    pub owner_id: String,
    pub breeder_id: String,
    pub dam_id: String,
    pub sire_id: String,
    pub has_won: Option<f64>,
    pub has_placed: Option<f64>,
    pub gender: Option<String>,
    pub origin: Option<String>,
    pub rating: Option<f64>,
    pub is_nonrunner: bool,
    pub number: u8,
    pub ranking_label: u8,
    pub win_probability: Option<f64>,
    pub age: u8,
    pub weight: f64,
    pub momentum: Option<f64>,
    pub place_percentile: Option<f64>,
    pub competitors_beaten_probability: Option<f64>,
    pub relative_distance_behind: Option<f64>,
    pub purse: i32,
    pub place: i32,
}

#[derive(Debug, Deserialize, PartialEq)]
pub struct RaceCard {
    pub date_time: String,
    pub country: String,
    pub day: u8,
    pub id: u32,
    pub n_runners: f64,
    pub distance: u16,
    pub race_type: String,
    pub race_class: String,
    pub surface: String,
    pub track_name: String,
    pub horses: HashMap<String, Horse>,
}

pub fn json_to_race_cards(json_data: &str) -> serde_json::Result<Vec<RaceCard>> {
    let racecards_map: HashMap<String, RaceCard> = serde_json::from_str(json_data)?;
    let racecards: Vec<RaceCard> = racecards_map.into_values().collect();

    Ok(racecards)
}
