use crate::stream_data::file_reading::deserialize::{Horse, RaceCard};
use crate::stream_data::value_calculator::ValueCalculator;
use std::collections::HashMap;
use crate::stream_data::category_calculators::CategoryCalculator;
use std::sync::Arc;

pub trait Feature {
    fn name(&self) -> String;
    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> Option<f64>;
}

pub struct FeatureExtractor {
    pub value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
    pub category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>,
    pub name: String
}

impl FeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        let mut name = value_calculator.name().to_string();

        if !category_calculators.is_empty() {
            name.push('_');
            for (i, category_calculator)
            in category_calculators.iter().enumerate() {
                name.push_str(&category_calculator.name());
                if i < category_calculators.len() - 1 {
                    name.push('_');
                }
            }
        }

        FeatureExtractor { value_calculator, category_calculators, name }
    }

    pub fn get_category_key(&mut self, race_card: &RaceCard, horse: &Horse) -> String {
        let mut category_key = String::new();

        for category_calculator in &self.category_calculators {
            let category = category_calculator.get_category(race_card, horse);
            category_key.push_str(&category);
        }

        category_key
    }
}

impl Feature for FeatureExtractor {
    fn name(&self) -> String {
        self.name.to_string()
    }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        self.value_calculator.calculate(race_card, horse)
    }
}


pub struct MaxFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub max_values: HashMap<String, Option<f64>>,
}

impl MaxFeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        MaxFeatureExtractor {
            feature_extractor: FeatureExtractor::new(value_calculator, category_calculators),
            max_values: HashMap::new()
        }
    }
}

impl Feature for MaxFeatureExtractor {
    fn name(&self) -> String { format!("{}{}", "max_", &self.feature_extractor.name()) }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let value = self.feature_extractor.value_calculator.calculate(race_card, horse);
        let max_value = self.max_values.entry(category_key).or_insert(None);

        let value = match value {
            Some(v) => v,
            None => return *max_value,
        };

        let result = *max_value;
        if max_value.is_none() || value > max_value.unwrap() {
            *max_value = Some(value);
        }

        result
    }
}

pub struct PreviousFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub previous_values: HashMap<String, Option<f64>>,
}

impl PreviousFeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        PreviousFeatureExtractor {
            feature_extractor: FeatureExtractor::new(value_calculator, category_calculators),
            previous_values: HashMap::new()
        }
    }
}

impl Feature for PreviousFeatureExtractor {
    fn name(&self) -> String { format!("{}{}", "previous_", &self.feature_extractor.name()) }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let value = self.feature_extractor.value_calculator.calculate(race_card, horse);
        let previous_value = self.previous_values.entry(category_key).or_insert(None);

        let old_value = *previous_value;
        *previous_value = value;

        old_value
    }
}

pub struct SimpleAverageFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub average_values: HashMap<String, Option<f64>>,
    pub count_values: HashMap<String, i32>
}

impl SimpleAverageFeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        SimpleAverageFeatureExtractor {
            feature_extractor: FeatureExtractor::new(value_calculator, category_calculators),
            average_values: HashMap::new(),
            count_values: HashMap::new()
        }
    }
}

impl Feature for SimpleAverageFeatureExtractor {
    fn name(&self) -> String { format!("{}{}", "simple_average_", &self.feature_extractor.name()) }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> Option<f64> {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let new_obs = self.feature_extractor.value_calculator.calculate(race_card, horse);

        let average = self.average_values.entry(category_key.clone()).or_insert(None);
        let count = self.count_values.entry(category_key).or_insert(0);

        let new_obs = match new_obs {
            Some(v) => v,
            None => return *average,
        };

        let result = *average;

        *count += 1;
        *average = match *average {
            Some(avg) => Some(((*count - 1) as f64 * avg + new_obs) / *count as f64),
            None => Some(new_obs),
        };

        result
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
