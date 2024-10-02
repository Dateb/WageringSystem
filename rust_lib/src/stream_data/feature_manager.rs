use crate::stream_data::feature_extractor::FeatureExtractor;
use crate::stream_data::value_calculator::AgeCalculator;
use std::rc::Rc;

pub struct FeatureManager {
    pub feature_extractors: Vec<FeatureExtractor>,
}

impl FeatureManager {
    pub fn new() -> Self {
        let age_calculator = Box::new(AgeCalculator);

        let feature_extractor_1 = FeatureExtractor::new(
            String::from("Age 1"),
            age_calculator.clone()
        );
        let feature_extractor_2 = FeatureExtractor::new(
            String::from("Age 2"),
            age_calculator
        );

        FeatureManager {
            feature_extractors: vec![feature_extractor_1, feature_extractor_2],
        }
    }
}
