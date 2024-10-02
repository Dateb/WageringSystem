pub(crate) mod deserialize;

use std::fs::File;
use std::fs;
use std::io::Read;
use std::path::PathBuf;
use crate::stream_data::file_reading::deserialize::*;

pub struct FileSplitter {
    pub train_files: Vec<PathBuf>,  // Holds paths to training files
    pub test_files: Vec<PathBuf>,   // Holds paths to testing files
}

impl FileSplitter {
    pub fn new(directory_path: &str, train_fraction: f64) -> Self {
        let mut files: Vec<PathBuf> = fs::read_dir(directory_path)
            .expect("Failed to read directory")
            .filter_map(|entry| entry.ok())  // Ignore errors during directory traversal
            .filter(|entry| entry.path().extension().and_then(|ext| ext.to_str()) == Some("json"))  // Only JSON files
            .map(|entry| entry.path())
            .collect();

        files.sort();

        let split_index = (files.len() as f64 * train_fraction).ceil() as usize;

        let train_files = files[..split_index].to_vec();
        let test_files = files[split_index..].to_vec();

        FileSplitter {
            train_files,
            test_files,
        }
    }
}

pub struct FileReader {
    files: Vec<PathBuf>,
    current: usize,
}

impl FileReader {

    pub fn new(file_paths: Vec<PathBuf>) -> Self {
        FileReader {
            files: file_paths,
            current: 0,
        }
    }

    // Reads and processes a file at a given index
    fn read_race_cards(&self, index: usize) -> Vec<RaceCard> {
        let file_path = &self.files[index];

        let mut file = File::open(file_path)
            .unwrap_or_else(|e| panic!("Failed to open file {}: {:?}", file_path.display(), e));

        let mut contents = String::new();
        file.read_to_string(&mut contents)
            .unwrap_or_else(|e| panic!("Failed to read file {}: {:?}", file_path.display(), e));

        // Convert the JSON data to Vec<Racecard>
        json_to_race_cards(&contents)
            .unwrap_or_else(|e| panic!("Failed to parse JSON in file {}: {:?}", file_path.display(), e))
    }
}

// Implementing the Iterator trait for FileReader
impl Iterator for FileReader {
    type Item = Vec<RaceCard>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.current < self.files.len() {
            let racecards = self.read_race_cards(self.current);
            self.current += 1;
            Some(racecards)
        } else {
            None // End of iteration
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;

    fn setup_test_file(file_name: &str, content: &str) -> PathBuf {
        let path = PathBuf::from(file_name);
        let mut file = File::create(&path).expect("Failed to create test file");
        file.write_all(content.as_bytes()).expect("Failed to write to test file");
        path
    }

    // Helper function to create test files
    fn setup_test_files(test_dir: &str, file_names: Vec<&str>) {
        std::fs::create_dir_all(test_dir).expect("Failed to create test directory");
        for file_name in file_names {
            let file_path = format!("{}/{}", test_dir, file_name);
            let mut file = File::create(file_path).expect("Failed to create test file");
            writeln!(file, "{{\"key\": \"value\"}}").expect("Failed to write to test file");
        }
    }

    #[test]
    fn test_file_splitter() {
        let test_dir = "test_splitter_dir";
        setup_test_files(test_dir, vec![
            "file1.json", "file2.json", "file3.json", "file4.json", "file5.json"
        ]);

        // Use FileSplitter with a 60% train fraction
        let file_splitter = FileSplitter::new(test_dir, 0.6);

        // Assert that the split is correct
        assert_eq!(file_splitter.train_files.len(), 3);  // 60% of 5 files is 3
        assert_eq!(file_splitter.test_files.len(), 2);   // 40% of 5 files is 2

        // Check that files are properly sorted and split
        assert!(file_splitter.train_files[0].ends_with("file1.json"));
        assert!(file_splitter.train_files[1].ends_with("file2.json"));
        assert!(file_splitter.train_files[2].ends_with("file3.json"));

        assert!(file_splitter.test_files[0].ends_with("file4.json"));
        assert!(file_splitter.test_files[1].ends_with("file5.json"));

        // Clean up
        fs::remove_dir_all(test_dir).expect("Failed to clean up test directory");
    }
}
