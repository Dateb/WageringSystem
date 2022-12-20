import json
import time

VALUE_MONITOR_DATA_PATH = "/home/daniel/PycharmProjects/horsacle/src/data/horse_data.json"


def main():
    print("hey")
    monitor_data = [
        {"id": 1, "win_prob": 0.25},
        {"id": 2, "win_prob": 0.75}
    ]
    while True:
        with open(VALUE_MONITOR_DATA_PATH, 'w') as fp:
            json.dump(monitor_data, fp)

        print("changed monitor data")
        time.sleep(5)


if __name__ == '__main__':
    main()
    print("finished")
