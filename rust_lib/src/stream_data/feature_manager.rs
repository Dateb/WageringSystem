use crate::stream_data::category_calculators::{CategoryCalculator, HorseIdCategory};
use crate::stream_data::feature_extractor::{Feature, FeatureExtractor, MaxFeatureExtractor, PreviousFeatureExtractor};
use crate::stream_data::value_calculator::{ValueCalculator, AgeCalculator, WeightCalculator, WinProbabilityCalculator};
use std::sync::Arc;
use serde::Deserialize;

pub struct FeatureManager {
    pub feature_extractors: Vec<Box<dyn Feature + Send + Sync>>,
}

#[derive(Deserialize)]
struct Config {
    feature_extractors: Vec<FeatureConfig>,
}

#[derive(Deserialize)]
struct FeatureConfig {
    extractor_type: String,
    value_calculator: String,
    categories: Option<Vec<String>>,
}

impl FeatureManager {
    pub fn from_config(config_json: &str) -> Self {
        let config: Config = serde_json::from_str(config_json).expect("Invalid JSON format");

        let mut feature_extractors: Vec<Box<dyn Feature + Send + Sync>> = Vec::new();

        for feature_extractor in config.feature_extractors {
            let value_calculator: Arc<dyn ValueCalculator + Send + Sync> = match feature_extractor.value_calculator.as_str() {
                "AgeCalculator" => Arc::new(AgeCalculator),
                "WeightCalculator" => Arc::new(WeightCalculator),
                "WinProbabilityCalculator" => Arc::new(WinProbabilityCalculator),
                _ => panic!("Unknown calculator type: {}", feature_extractor.value_calculator),
            };

            // Match extractor type
            let extractor: Box<dyn Feature + Send + Sync> = match feature_extractor.extractor_type.as_str() {
                "FeatureExtractor" => Box::new(FeatureExtractor::new(value_calculator.clone(), vec![])),
                "MaxFeatureExtractor" => Box::new(MaxFeatureExtractor::new(
                    value_calculator.clone(),
                    parse_categories(&feature_extractor.categories)
                )),
                "PreviousFeatureExtractor" => Box::new(PreviousFeatureExtractor::new(
                    value_calculator.clone(),
                    parse_categories(&feature_extractor.categories)
                )),
                _ => panic!("Unknown extractor type: {}", feature_extractor.extractor_type),
            };

            feature_extractors.push(extractor);
        }

        FeatureManager {
            feature_extractors,
        }
    }

    pub fn get_feature_names(&self) -> Vec<String> {
        self.feature_extractors
            .iter()
            .map(|extractor| extractor.name().to_string())
            .collect()
    }
}


fn parse_categories(category_names: &Option<Vec<String>>) -> Vec<Arc<dyn CategoryCalculator + Send + Sync>> {
    let mut categories: Vec<Arc<dyn CategoryCalculator + Send + Sync>> = Vec::new();

    if let Some(category_names) = category_names {
        for category_name in category_names {
            let category_calculator: Arc<dyn CategoryCalculator + Send + Sync> = match category_name.as_str() {
                "HorseIdCategory" => Arc::new(HorseIdCategory),
                _ => panic!("Unknown category: {}", category_name),
            };
            categories.push(category_calculator);
        }
    }

    categories
}
