from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.RawRaceCardInjector import past_form_track_to_win_time_track
from Persistence.JSONPersistence import JSONPersistence
from SampleExtraction.Sources.FeatureSource import FeatureSource
from util.nested_dict import nested_dict


class SpeedFiguresSource(FeatureSource):

    BASE_SPEED = 0

    def __init__(self):
        super().__init__()
        self.__base_times = nested_dict()
        self.__par_figures = nested_dict()
        self.__speed_figures = nested_dict()
        self.__win_times = JSONPersistence("win_times_contextualized").load()

    def update(self, race_card: RaceCard):
        self.__compute_base_times(race_card)
        self.__compute_points_per_second()
        self.__compute_par_figures(race_card)
        self.__compute_speed_figures(race_card)

    def get_current_speed_figure(self, horse: Horse):
        if horse.name not in self.__speed_figures:
            return -1

        return self.__speed_figures[horse.name]["avg"]

    def __compute_base_times(self, race_card: RaceCard):
        win_time = race_card.race_result.win_time
        distance_key = str(race_card.distance)

        if win_time > 0:
            self.update_average(category=self.__base_times[distance_key], new_obs=win_time)

    def __compute_points_per_second(self):
        for distance in self.__base_times:
            self.__base_times[distance]["points per second"] = (1 / self.__base_times[distance]["avg"]) * 100 * 10

    def __compute_par_figures(self, race_card: RaceCard):
        win_time = race_card.race_result.win_time
        distance_key = str(race_card.distance)
        race_class_key = str(race_card.race_class)
        if win_time > 0:
            base_time_of_distance = self.__base_times[distance_key]["avg"]
            points_per_second_of_distance = self.__base_times[distance_key]["points per second"]
            seconds_difference = base_time_of_distance - win_time
            par_figure = self.BASE_SPEED + seconds_difference * points_per_second_of_distance

            self.update_average(category=self.__par_figures[distance_key][race_class_key], new_obs=par_figure)

    def __compute_speed_figures(self, race_card: RaceCard):
        for horse in race_card.horses:
            speed_figure = self.__compute_speed_figure(race_card, horse)
            self.update_average(category=self.__speed_figures[horse.name], new_obs=speed_figure)

    def __compute_speed_figure(self, race_card: RaceCard, horse: Horse) -> float:
        # TODO: collect more past winning times (distance != 1 check is then not necessary anymore)
        if horse.horse_distance == -1 or race_card.distance == -1:
            return -1

        if str(race_card.distance) not in self.__base_times:
            return -1

        seconds_behind_winner = ((1 / self.__get_lengths_per_second(race_card)) * horse.horse_distance)

        horse_time = race_card.race_result.win_time + seconds_behind_winner
        base_time = self.__base_times[str(race_card.distance)]["avg"]
        seconds_difference = base_time - horse_time

        points_per_second = self.__base_times[str(race_card.distance)]["points per second"]

        track_variant = self.__get_track_variant(str(race_card.date), race_card.track_name)

        horse_speed_figure = self.BASE_SPEED + seconds_difference * points_per_second + track_variant
        # if horse_speed_figure < -250:
        #     print(f"horse_time:{horse_time}")
        #     print(f"base_time:{base_time}")
        #     print(f"points_per_second:{points_per_second}")
        #     print(f"track_variant:{track_variant}")
        #     print("----------------------------------------")
        if horse_speed_figure < -250:
            return -250

        if horse_speed_figure > 250:
            return 250

        return horse_speed_figure

    def __get_track_variant(self, date: str, track_name: str):
        track_figure_biases = []

        # TODO: just a quick and dirty mapping. The win times data should rename its track names after the ones on racebets.
        track_name = past_form_track_to_win_time_track(track_name)

        for race in self.__win_times[date][track_name]:
            race_distance = str(self.__win_times[date][track_name][race]["distance"])

            if race_distance in self.__base_times:
                race_class = self.__win_times[date][track_name][race]["class"]
                win_time = self.__win_times[date][track_name][race]["win_time"]

                if win_time > 0:
                    base_time = self.__base_times[race_distance]["avg"]
                    points_per_second = self.__base_times[race_distance]["points per second"]

                    seconds_difference = base_time - win_time

                    win_figure = self.BASE_SPEED + seconds_difference * points_per_second
                    if race_class in self.__par_figures[race_distance]:
                        par_figure = self.__par_figures[race_distance][race_class]["avg"]

                        track_figure_biases.append(par_figure - win_figure)
                        if (par_figure - win_figure) < -250:
                            print("-------------------------------")
                            print(f"date:{date}")
                            print(f"track_name:{track_name}")
                            print(f"race_distance:{race_distance}")
                            print(f"base_time:{base_time}")
                            print(f"win_time:{win_time}")
                            print(f"seconds_difference:{seconds_difference}")
                            print(f"points_per_second:{points_per_second}")
                            print(f"par figure: {par_figure}")
                            print(f"win figure: {win_figure}")
                            print("---------------------------------")

        if track_figure_biases:
            return sum(track_figure_biases) / len(track_figure_biases)
        else:
            return 0

    def __get_lengths_per_second(self, race_card: RaceCard) -> float:
        if race_card.race_type == "G":
            if race_card.surface == "TRF":
                if race_card.going <= 3:
                    return 6
                if race_card.going >= 4:
                    return 5
            if race_card.surface == "EQT":
                if race_card.track_name in ["Kempton", "Lingfield", "Wolverhampton", "Newcastle", "Chelmsford", "Chelmsford City"]:
                    return 6
                if race_card.track_name in ["Southwell"]:
                    return 5
                # TODO: Chelmsford and Chelmsford are in the data
                print(race_card.track_name)
                print(race_card.race_id)
        if race_card.race_type == "J":
            if race_card.going <= 3:
                return 5
            if race_card.going >= 4:
                return 4
            return 4.5

        return 5.0


#gut-fest: 2.5
#gut: 3
#gut-weich: 3.5
#weich: 4

__feature_source: SpeedFiguresSource = SpeedFiguresSource()


def get_feature_source() -> SpeedFiguresSource:
    return __feature_source
