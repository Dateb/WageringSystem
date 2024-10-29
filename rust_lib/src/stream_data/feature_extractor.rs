use crate::stream_data::file_reading::deserialize::{Horse, RaceCard};
use crate::stream_data::value_calculator::{FeatureValue, ValueCalculator};
use std::collections::HashMap;
use crate::stream_data::category_calculators::CategoryCalculator;
use std::sync::Arc;
use chrono::{Datelike, NaiveDateTime};

pub trait Feature {
    fn name(&self) -> String;
    fn is_categorical(&self) -> bool;
    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue;
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
    fn is_categorical(&self) -> bool { self.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        self.value_calculator.calculate(race_card, horse)
    }
}


pub struct MaxFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub max_values: HashMap<String, FeatureValue>,
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
    fn is_categorical(&self) -> bool { self.feature_extractor.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let value = self.feature_extractor.value_calculator.calculate(race_card, horse);
        let max_value = self.max_values.entry(category_key).or_insert(FeatureValue::None);

        let value = match value {
            FeatureValue::Number(v) => v,
            _ => return max_value.clone(),
        };

        let result = max_value.clone();
        match max_value {
            FeatureValue::Number(current_max) => {
                if value > *current_max {
                    *max_value = FeatureValue::Number(value);
                }
            },
            FeatureValue::None => {
                *max_value = FeatureValue::Number(value);
            },
            _ => {},
        };

        result
    }
}

pub struct PreviousFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub previous_values: HashMap<String, FeatureValue>,
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
    fn is_categorical(&self) -> bool { self.feature_extractor.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let value = self.feature_extractor.value_calculator.calculate(race_card, horse);
        let previous_value = self.previous_values.entry(category_key).or_insert(FeatureValue::None);

        let old_value = previous_value.clone();

        *previous_value = match value {
            FeatureValue::Number(num) => FeatureValue::Number(num),
            FeatureValue::Text(text) => FeatureValue::Text(text),
            FeatureValue::None => previous_value.clone()
        };

        old_value
    }
}

pub struct SumFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub sum_values: HashMap<String, FeatureValue>,
}

impl SumFeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        SumFeatureExtractor {
            feature_extractor: FeatureExtractor::new(value_calculator, category_calculators),
            sum_values: HashMap::new()
        }
    }
}

impl Feature for SumFeatureExtractor {
    fn name(&self) -> String { format!("{}{}", "sum_", &self.feature_extractor.name()) }
    fn is_categorical(&self) -> bool { self.feature_extractor.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let value = self.feature_extractor.value_calculator.calculate(race_card, horse);
        let sum_value = self.sum_values.entry(category_key).or_insert(FeatureValue::Number(0.0));

        let result = sum_value.clone();
        *sum_value = value.add(sum_value);

        result
    }
}

pub struct SimpleAverageFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub average_values: HashMap<String, FeatureValue>,
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
    fn is_categorical(&self) -> bool { self.feature_extractor.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let feature_value = self.feature_extractor.value_calculator.calculate(race_card, horse);

        let average = self.average_values.entry(category_key.clone()).or_insert(FeatureValue::None);
        let count = self.count_values.entry(category_key).or_insert(0);

        let new_obs = match feature_value {
            FeatureValue::Number(v) => v,
            _ => return average.clone(),
        };

        let result = average.clone();

        *count += 1;
        *average = match *average {
            FeatureValue::Number(avg) => FeatureValue::Number(((*count - 1) as f64 * avg + new_obs) / *count as f64),
            _ => FeatureValue::Number(new_obs),
        };

        result
    }
}

pub struct EMAFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub average_values: HashMap<String, FeatureValue>,
    decay_factor: f64
}

impl EMAFeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        let decay_factor = 0.01;
        EMAFeatureExtractor {
            feature_extractor: FeatureExtractor::new(value_calculator, category_calculators),
            average_values: HashMap::new(),
            decay_factor
        }
    }
}

impl Feature for EMAFeatureExtractor {
    fn name(&self) -> String { format!("{}{}", "EMA_", &self.feature_extractor.name()) }
    fn is_categorical(&self) -> bool { self.feature_extractor.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let feature_value = self.feature_extractor.value_calculator.calculate(race_card, horse);

        let average = self.average_values.entry(category_key.clone()).or_insert(FeatureValue::None);

        let new_obs = match feature_value {
            FeatureValue::Number(v) => v,
            _ => return average.clone(),
        };

        let result = average.clone();

        *average = match *average {
            FeatureValue::Number(avg) => {
                FeatureValue::Number(self.decay_factor * new_obs + (1.0 - self.decay_factor) * avg)
            },
            _ => FeatureValue::Number(new_obs),
        };

        result
    }
}

pub struct EMADayDecayFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub average_values: HashMap<String, FeatureValue>,
    pub previous_race_day: HashMap<String, FeatureValue>,
    decay_factor: f64
}

impl EMADayDecayFeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        let decay_factor = 0.01;
        EMADayDecayFeatureExtractor {
            feature_extractor: FeatureExtractor::new(value_calculator, category_calculators),
            average_values: HashMap::new(),
            previous_race_day: HashMap::new(),
            decay_factor
        }
    }
}

impl Feature for EMADayDecayFeatureExtractor {
    fn name(&self) -> String { format!("{}{}", "EMADayDecay_", &self.feature_extractor.name()) }
    fn is_categorical(&self) -> bool { self.feature_extractor.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let feature_value = self.feature_extractor.value_calculator.calculate(race_card, horse);

        let average = self.average_values.entry(category_key.clone()).or_insert(FeatureValue::None);
        let previous_race_day = self.previous_race_day.entry(category_key).or_insert(FeatureValue::None);

        let new_obs = match feature_value {
            FeatureValue::Number(v) => v,
            _ => return average.clone(),
        };

        let result = average.clone();

        let weight_old = match previous_race_day {
            FeatureValue::Number(previous_race_day) => {
                let datetime =
                    NaiveDateTime::parse_from_str(&race_card.date_time, "%Y-%m-%d %H:%M:%S")
                        .expect("Failed to parse date");
                let current_race_day = datetime.num_days_from_ce() as f64;
                let n_days_since_last_obs = current_race_day - *previous_race_day;
                (-self.decay_factor * (n_days_since_last_obs + 1.0)).exp()
            }
            _ => 0.0
        };
        *average = match *average {
            FeatureValue::Number(avg) => {
                let weight_new = 1.0 - weight_old;
                let new_average = (weight_old * avg + weight_new * new_obs) / (weight_old + weight_new);
                FeatureValue::Number(new_average)
            },
            _ => FeatureValue::Number(new_obs),
        };

        result
    }
}

pub struct ActExpFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub actual_sum: HashMap<String, f64>,
    pub expected_sum: HashMap<String, f64>
}

impl ActExpFeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        ActExpFeatureExtractor {
            feature_extractor: FeatureExtractor::new(value_calculator, category_calculators),
            actual_sum: HashMap::new(),
            expected_sum: HashMap::new()
        }
    }
}

impl Feature for ActExpFeatureExtractor {
    fn name(&self) -> String { format!("{}{}", "ActExp_", &self.feature_extractor.name()) }
    fn is_categorical(&self) -> bool { self.feature_extractor.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);

        let actual_sum = self.actual_sum.entry(category_key.clone()).or_insert(0.0);
        let expected_sum = self.expected_sum.entry(category_key).or_insert(0.0);

        let result = match expected_sum {
            0.0 => -1.0,
            _ => *actual_sum / *expected_sum
        };

        *actual_sum = match horse.has_won {
            Some(has_won) => *actual_sum + has_won,
            None => *actual_sum
        };
        *expected_sum = match horse.win_probability {
            Some(win_probability) => *expected_sum + win_probability,
            None => *expected_sum,
        };

        FeatureValue::Number(result)
    }
}

pub struct DiffPreviousFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub previous_values: HashMap<String, FeatureValue>,
}

impl DiffPreviousFeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        DiffPreviousFeatureExtractor {
            feature_extractor: FeatureExtractor::new(value_calculator, category_calculators),
            previous_values: HashMap::new(),
        }
    }
}

impl Feature for DiffPreviousFeatureExtractor {
    fn name(&self) -> String { format!("{}{}", "DiffPrevious_", &self.feature_extractor.name()) }
    fn is_categorical(&self) -> bool { self.feature_extractor.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let feature_value = self.feature_extractor.value_calculator.calculate(race_card, horse);
        let previous_value = self.previous_values.entry(category_key).or_insert(FeatureValue::None);

        let result = feature_value.subtract(previous_value);
        *previous_value = feature_value;

        result
    }
}

pub struct DiffAverageFeatureExtractor {
    pub feature_extractor: FeatureExtractor,
    pub average_values: HashMap<String, FeatureValue>,
    pub count_values: HashMap<String, i32>,
}

impl DiffAverageFeatureExtractor {
    pub fn new(
        value_calculator: Arc<dyn ValueCalculator + Send + Sync>,
        category_calculators: Vec<Arc<dyn CategoryCalculator + Send + Sync>>
    ) -> Self {
        DiffAverageFeatureExtractor {
            feature_extractor: FeatureExtractor::new(value_calculator, category_calculators),
            average_values: HashMap::new(),
            count_values: HashMap::new(),
        }
    }
}

impl Feature for DiffAverageFeatureExtractor {
    fn name(&self) -> String { format!("{}{}", "DiffAverage_", &self.feature_extractor.name()) }
    fn is_categorical(&self) -> bool { self.feature_extractor.value_calculator.is_categorical() }

    fn extract(&mut self, race_card: &RaceCard, horse: &Horse) -> FeatureValue {
        let category_key = self.feature_extractor.get_category_key(&race_card, &horse);
        let feature_value = self.feature_extractor.value_calculator.calculate(race_card, horse);

        let average = self.average_values.entry(category_key.clone()).or_insert(FeatureValue::None);
        let count = self.count_values.entry(category_key).or_insert(0);

        let new_obs = match feature_value {
            FeatureValue::Number(v) => v,
            _ => return FeatureValue::None,
        };

        let result = feature_value.subtract(average);

        *count += 1;
        *average = match *average {
            FeatureValue::Number(avg) => FeatureValue::Number(((*count - 1) as f64 * avg + new_obs) / *count as f64),
            _ => FeatureValue::Number(new_obs),
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
