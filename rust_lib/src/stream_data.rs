mod file_reading;
mod value_calculator;
mod feature_extractor;
mod feature_manager;

use std::cmp;
use std::collections::HashMap;
use std::path::PathBuf;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde::Serialize;
use crate::stream_data::feature_manager::FeatureManager;
use crate::stream_data::file_reading::deserialize::RaceCard;
use crate::stream_data::file_reading::{FileReader, FileSplitter};

#[derive(Serialize)]
pub struct StreamData {
    date_time: Vec<String>,
    race_id: Vec<u32>,
    number: Vec<u8>,
    place: Vec<i32>,
    ranking_label: Vec<i32>,
    features: HashMap<String, Vec<f64>>
}

impl StreamData {
    fn new() -> Self {
        StreamData {
            date_time: vec![],
            race_id: vec![],
            number: vec![],
            place: vec![],
            ranking_label: vec![],
            features: HashMap::new(),
        }
    }

    fn add_race_cards(&mut self, race_cards: Vec<RaceCard>, feature_manager: &FeatureManager) {
        for race_card in race_cards {
            for horse in race_card.horses.values() {
                self.date_time.push(race_card.date_time.clone());
                self.race_id.push(race_card.id);
                self.number.push(horse.number);
                self.place.push(horse.place);

                let ranking_label = match horse.place {
                    p if p > 0 => cmp::max(30 - p, 0),
                    _ => 0,
                };
                self.ranking_label.push(ranking_label);

                for feature_extractor in &feature_manager.feature_extractors {
                    let feature_name = feature_extractor.name().to_string();
                    let feature_value = feature_extractor.value_calculator.calculate(&race_card, horse);

                    self.features
                        .entry(feature_name)
                        .or_insert_with(Vec::new)
                        .push(feature_value);
                }
            }
        }
    }

    pub fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<&'py PyDict> {
        let dict = PyDict::new(py);

        let date_times = PyList::new(py, &self.date_time);
        let race_ids = PyList::new(py, &self.race_id);
        let numbers = PyList::new(py, &self.number);
        let places = PyList::new(py, &self.place);
        let ranking_labels = PyList::new(py, &self.ranking_label);

        dict.set_item("date_time", date_times)?;
        dict.set_item("race_id", race_ids)?;
        dict.set_item("number", numbers)?;
        dict.set_item("place", places)?;
        dict.set_item("ranking_label", ranking_labels)?;

        for (feature_name, feature_values) in &self.features {
            let py_feature_values = PyList::new(py, feature_values);
            dict.set_item(feature_name, py_feature_values)?;
        }

        Ok(dict)
    }
}


#[pyfunction]
fn get_stream_data_dict(py: Python) -> PyResult<&PyDict> {
    let mut stream_data = StreamData::new();

    let file_splitter = FileSplitter::new(
        "../data/race_cards_dev",
        0.8
    );

    let train_file_reader = FileReader::new(file_splitter.train_files);
    let test_file_reader = FileReader::new(file_splitter.test_files);

    let feature_manager = FeatureManager::new();

    for race_cards in train_file_reader {
        stream_data.add_race_cards(race_cards, &feature_manager);
    }

    for race_cards in test_file_reader {
        stream_data.add_race_cards(race_cards, &feature_manager);
    }

    stream_data.to_dict(py)
}

#[pyclass]
pub struct StreamDataManager {
    file_splitter: FileSplitter,
    feature_manager: FeatureManager,
}

#[pymethods]
impl StreamDataManager {
    #[new]
    pub fn new(directory_path: &str, train_fraction: f64) -> Self {
        let file_splitter = FileSplitter::new(directory_path, train_fraction);
        let feature_manager = FeatureManager::new();
        StreamDataManager { file_splitter, feature_manager }
    }

    pub fn get_train_stream_data(&self, py: Python) -> PyResult<PyObject> {
        self.get_stream_data(py, self.file_splitter.train_files.clone())
    }

    pub fn get_test_stream_data(&self, py: Python) -> PyResult<PyObject> {
        self.get_stream_data(py, self.file_splitter.test_files.clone())
    }

    fn get_stream_data(&self, py: Python, files: Vec<PathBuf>) -> PyResult<PyObject> {
        let mut stream_data = StreamData::new();

        let test_file_reader = FileReader::new(files);

        for race_cards in test_file_reader {
            stream_data.add_race_cards(race_cards, &self.feature_manager);
        }

        let py_dict = stream_data.to_dict(py)?;  // Obtain the PyDict

        // Convert &PyDict to PyObject using Py::from
        Ok(Py::from(py_dict))
    }
}



#[cfg(test)]
mod tests {}

#[pymodule]
pub fn stream_data(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<StreamDataManager>()?;
    Ok(())
}
