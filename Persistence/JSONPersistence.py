import json
import os


class JSONPersistence:
    def __init__(self, file_name: str):
        self.__FILE_NAME = f"../data/{file_name}.json"

    def save(self, save_data: dict):
        print("writing...")
        with open(self.__FILE_NAME, "w") as f:
            json.dump(save_data, f)
        print("writing done")

    def load(self) -> dict:
        if not os.path.isfile(self.__FILE_NAME):
            print("File not found. Returning empty dict.")
            return {}

        with open(self.__FILE_NAME, "r") as f:
            load_data = json.load(f)

        return load_data
