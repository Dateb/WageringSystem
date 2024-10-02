use crate::stream_data::file_reading::deserialize::{Horse, RaceCard};
use crate::stream_data::value_calculator::{AgeCalculator, ValueCalculator};

pub struct FeatureExtractor {
    pub name: String,
    pub value_calculator: Box<dyn ValueCalculator + Send + Sync>,
}

impl FeatureExtractor {
    pub fn new(name: String, value_calculator: Box<dyn ValueCalculator + Send + Sync>) -> Self {
        FeatureExtractor { name, value_calculator }
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn extract(&self, race_card: &RaceCard, horse: &Horse) -> f64 {
        self.value_calculator.calculate(race_card, horse)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    // Mock data for testing
    fn create_race_card() -> RaceCard {
        let mut horses = HashMap::new();
        horses.insert(
            "Horse 1".to_string(),
            Horse {
                number: 1,
                age: 5,
                place: 2,
            },
        );
        horses.insert(
            "Horse 2".to_string(),
            Horse {
                number: 2,
                age: 7,
                place: 1,
            },
        );

        RaceCard {
            date_time: "2024-09-30T12:34:56".to_string(),
            id: 42,
            horses,
        }
    }

    #[test]
    fn test_age_calculator() {
        let race_card = create_race_card();
        let horse = race_card.horses.get("Horse 1").unwrap();

        // Create AgeCalculator instance
        let age_calculator = Box::new(AgeCalculator);

        // Create FeatureExtractor with AgeCalculator
        let feature_extractor = FeatureExtractor::new(age_calculator);

        // Extract the age feature
        let age_value = feature_extractor.extract(&race_card, horse);

        // Assert that the extracted value is correct
        assert_eq!(age_value, 5.0);
    }

    #[test]
    fn test_age_calculator_with_different_horse() {
        let race_card = create_race_card();
        let horse = race_card.horses.get("Horse 2").unwrap();
        let age_calculator = Box::new(AgeCalculator);

        let feature_extractor = FeatureExtractor::new(age_calculator);

        let age_value = feature_extractor.extract(&race_card, horse);

        assert_eq!(age_value, 7.0);
    }
}
