use std::collections::HashMap;
use serde::Deserialize;

#[derive(Debug, Deserialize, PartialEq)]
pub struct Horse {
    pub id: u32,
    pub number: u8,
    pub sp: f64,
    pub age: u8,
    pub weight: f64,
    pub place: i32,
}

#[derive(Debug, Deserialize, PartialEq)]
pub struct RaceCard {
    pub date_time: String,
    pub id: u32,
    pub horses: HashMap<String, Horse>,
}

pub fn json_to_race_cards(json_data: &str) -> serde_json::Result<Vec<RaceCard>> {
    let racecards_map: HashMap<String, RaceCard> = serde_json::from_str(json_data)?;
    let racecards: Vec<RaceCard> = racecards_map.into_values().collect();

    Ok(racecards)
}
