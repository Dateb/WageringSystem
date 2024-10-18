import json
import os

from DataAbstraction.Present.RaceCard import RaceCard


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
            for raw_race_card in track_name_values.values():
                race_id = raw_race_card['race']['idRace']
                race_card = RaceCard(race_id, raw_race_card)

                race_key = str(race_card.datetime)
                new_dict[race_key] = {
                    "date_time": race_key,
                    "country": race_card.country,
                    "day": race_card.date.day,
                    "id": race_id,
                    "n_runners": race_card.n_runners,
                    "distance": race_card.adjusted_distance,
                    "going": race_card.going,
                    "race_type": race_card.race_type,
                    "race_class": race_card.race_class,
                    "surface": race_card.surface,
                    "track_name": race_card.track_name,
                }

                horses_dict = {}
                for horse in race_card.horses:
                    horses_dict[horse.horse_id] = {
                        "id": horse.subject_id,
                        "jockey_id": horse.jockey_id,
                        "trainer_id": horse.trainer_id,
                        "owner_id": horse.owner,
                        "breeder_id": horse.breeder,
                        "dam_id": horse.dam,
                        "sire_id": horse.sire,
                        "has_won": horse.has_won,
                        "has_placed": horse.has_placed,
                        "number": horse.number,
                        "is_nonrunner": horse.is_nonrunner,
                        "ranking_label": horse.ranking_label,
                        "win_probability": horse.sp_win_prob,
                        "age": horse.age,
                        "gender": horse.gender,
                        "origin": horse.origin,
                        "rating": horse.rating,
                        "has_visor": int("v" in horse.equipments),
                        "place": horse.place,
                        "weight": horse.jockey.weight,
                        "momentum": horse.momentum,
                        "place_percentile": horse.place_percentile,
                        "relative_distance_behind": horse.relative_distance_behind,
                        "competitors_beaten_probability": horse.competitors_beaten_probability,
                        "purse": horse.purse
                    }

                new_dict[race_key]['horses'] = horses_dict

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
