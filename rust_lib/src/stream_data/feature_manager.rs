use std::collections::HashMap;
use crate::stream_data::category_calculators::*;
use crate::stream_data::feature_extractor::*;
use crate::stream_data::value_calculator::*;
use std::sync::Arc;
use serde::Deserialize;

pub struct FeatureManager {
    pub feature_extractors: Vec<Box<dyn Feature + Send + Sync>>,
}

#[derive(Deserialize)]
struct Config {
    feature_extractors: HashMap<String, HashMap<String, Vec<Vec<String>>>>,
}

impl FeatureManager {
    pub fn from_config(config_json: &str) -> Self {
        let config: Config = serde_json::from_str(config_json).expect("Invalid JSON format");

        let mut feature_extractors: Vec<Box<dyn Feature + Send + Sync>> = Vec::new();

        for (extractor_type, calculators) in config.feature_extractors {
            for (value_calculator, categories_list) in calculators {
                let value_calculator: Arc<dyn ValueCalculator + Send + Sync> = match value_calculator.as_str() {
                    "Age" => Arc::new(AgeCalculator),
                    "Weight" => Arc::new(WeightCalculator),
                    "WinProbability" => Arc::new(WinProbabilityCalculator),
                    "PlacePercentile" => Arc::new(PlacePercentileCalculator),
                    "RelativeDistanceBehind" => Arc::new(RelativeDistanceBehindCalculator),
                    "Purse" => Arc::new(PurseCalculator),
                    _ => panic!("Unknown calculator type: {}", value_calculator),
                };

                for categories in categories_list {
                    let parsed_categories = parse_categories(&categories);

                    let extractor: Box<dyn Feature + Send + Sync> = match extractor_type.as_str() {
                        "Current" => Box::new(FeatureExtractor::new(value_calculator.clone(), parsed_categories)),
                        "Max" => Box::new(MaxFeatureExtractor::new(value_calculator.clone(), parsed_categories)),
                        "Previous" => Box::new(PreviousFeatureExtractor::new(value_calculator.clone(), parsed_categories)),
                        "SimpleAverage" => Box::new(SimpleAverageFeatureExtractor::new(value_calculator.clone(), parsed_categories)),
                        _ => panic!("Unknown extractor type: {}", extractor_type),
                    };

                    feature_extractors.push(extractor);
                }
            }
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


fn parse_categories(category_names: &Vec<String>) -> Vec<Arc<dyn CategoryCalculator + Send + Sync>> {
    let mut categories: Vec<Arc<dyn CategoryCalculator + Send + Sync>> = Vec::new();

    for category_name in category_names {
        let category_calculator: Arc<dyn CategoryCalculator + Send + Sync> = match category_name.as_str() {
            "HorseId" => Arc::new(HorseIdCategory),
            "JockeyId" => Arc::new(JockeyIdCategory),
            "TrainerId" => Arc::new(TrainerIdCategory),
            "OwnerId" => Arc::new(OwnerIdCategory),
            "BreederId" => Arc::new(BreederIdCategory),
            "RaceType" => Arc::new(RaceTypeCategory),
            "RaceClass" => Arc::new(RaceClassCategory),
            _ => panic!("Unknown category: {}", category_name),
        };
        categories.push(category_calculator);
    }

    categories
}
