import json
import os
from datetime import datetime


# 1. Read JSON file contents into a dict
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


# 2. Read a value from a key and write it into a new dict
def extract_value_to_new_dict(old_dict):
    new_dict = {}

    for race_day_values in old_dict.values():
        for track_name_values in race_day_values.values():
            for track_number_values in track_name_values.values():
                unix_post_time = track_number_values['race']["postTime"]
                post_time = datetime.utcfromtimestamp(unix_post_time).strftime('%Y-%m-%d %H:%M:%S')

                race_id = track_number_values['race']['idRace']
                new_dict[post_time] = {
                    "date_time": post_time,
                    "id": race_id,
                }

                horses = track_number_values['runners']['data']

                horses_dict = {}
                for horse_id, horse_values in horses.items():
                    place = int(horse_values.get("finalPosition", -1))

                    # DO: Fix this better in the future!!!!!
                    age = max([0, horse_values['age']])
                    jockey_data = horse_values["jockey"]
                    weight = jockey_data.get("weight", {}).get("weight", -1)
                    sp = horse_values.get("bsp_win", 0)

                    horses_dict[horse_id] = {
                        "id": horse_values["idSubject"],
                        "number": horse_values["programNumber"],
                        "sp": sp,
                        "age": age,
                        "place": place,
                        "weight": weight,
                    }

                new_dict[post_time]['horses'] = horses_dict

    return new_dict


# 3. Write the new dict into a new JSON file
def write_json_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


# 4. Process multiple files
def process_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in os.listdir(input_dir):
        if file_name.endswith('.json'):
            input_file = os.path.join(input_dir, file_name)
            output_file = os.path.join(output_dir, file_name)

            # Read the input JSON file
            data = read_json_file(input_file)

            # Extract the value from the given key and store it in a new dict
            extracted_data = extract_value_to_new_dict(data)

            # Write the new dict to the output JSON file
            write_json_file(extracted_data, output_file)

            print(f"Processed {input_file} and saved to {output_file}")


# Example usage
if __name__ == "__main__":
    input_directory = '../data/raw_race_cards_dev'
    output_directory = '../data/race_cards_dev'

    # Process all JSON files in the input directory
    process_files(input_directory, output_directory)
