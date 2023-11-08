from typing import List

from SampleExtraction.feature_sources.feature_sources import HorseNameToSubjectIdSource, WinProbabilitySource, \
    WinRateSource, AveragePlacePercentileSource, AverageRelativeDistanceBehindSource, ShowRateSource, PurseRateSource, \
    PercentageBeatenSource, ScratchedRateSource, MaxWinProbabilitySource, SpeedFiguresSource, DrawBiasSource, \
    HasFallenSource, FeatureSource
from SampleExtraction.feature_sources.previous_based import LifeTimeStartCountSource, LifeTimeWinCountSource, \
    LifeTimePlaceCountSource, PreviousWinProbSource, PreviousPlacePercentileSource, \
    PreviousRelativeDistanceBehindSource, PreviousTrackNameSource, PreviousDistanceSource, \
    PreviousRaceGoingSource, PreviousRaceClassSource, EquipmentAlreadyWornSource, PreviousTrainerSource, \
    PreviousDateSource, PreviousJockeySource

horse_name_to_subject_id_source: HorseNameToSubjectIdSource = HorseNameToSubjectIdSource()

# Average based sources:
win_probability_source:  WinProbabilitySource = WinProbabilitySource()
win_rate_source: WinRateSource = WinRateSource()

average_place_percentile_source: AveragePlacePercentileSource = AveragePlacePercentileSource()
average_place_percentile_source.average_attribute_groups.append(["name"])

sire_siblings_place_percentile_source: AveragePlacePercentileSource = AveragePlacePercentileSource()
sire_siblings_place_percentile_source.average_attribute_groups.append(["sire"])

dam_siblings_place_percentile_source: AveragePlacePercentileSource = AveragePlacePercentileSource()
dam_siblings_place_percentile_source.average_attribute_groups.append(["dam"])

sire_and_dam_siblings_place_percentile_source: AveragePlacePercentileSource = AveragePlacePercentileSource()
sire_and_dam_siblings_place_percentile_source.average_attribute_groups.append(["sire", "dam"])

dam_sire_siblings_place_percentile_source: AveragePlacePercentileSource = AveragePlacePercentileSource()
dam_sire_siblings_place_percentile_source.average_attribute_groups.append(["dam_sire"])

average_relative_distance_behind_source: AverageRelativeDistanceBehindSource = AverageRelativeDistanceBehindSource()
average_relative_distance_behind_source.average_attribute_groups.append(["name"])

show_rate_source: ShowRateSource = ShowRateSource()
purse_rate_source: PurseRateSource = PurseRateSource()


percentage_beaten_source: PercentageBeatenSource = PercentageBeatenSource()
scratched_rate_source: ScratchedRateSource = ScratchedRateSource()

life_time_start_count_source: LifeTimeStartCountSource = LifeTimeStartCountSource()
life_time_win_count_source: LifeTimeWinCountSource = LifeTimeWinCountSource()
life_time_place_count_source: LifeTimePlaceCountSource = LifeTimePlaceCountSource()

#Max based sources:
max_win_prob_source: MaxWinProbabilitySource = MaxWinProbabilitySource()

#Previous value based sources:
previous_jockey_source: PreviousJockeySource = PreviousJockeySource()

previous_win_prob_source: PreviousWinProbSource = PreviousWinProbSource()
previous_place_percentile_source: PreviousPlacePercentileSource = PreviousPlacePercentileSource()
previous_relative_distance_behind_source: PreviousRelativeDistanceBehindSource = PreviousRelativeDistanceBehindSource()
previous_track_name_source: PreviousTrackNameSource = PreviousTrackNameSource()

previous_distance_source: PreviousDistanceSource = PreviousDistanceSource()
previous_race_going_source: PreviousRaceGoingSource = PreviousRaceGoingSource()
previous_race_class_source: PreviousRaceClassSource = PreviousRaceClassSource()

equipment_already_worn_source: EquipmentAlreadyWornSource = EquipmentAlreadyWornSource()

previous_trainer_source: PreviousTrainerSource = PreviousTrainerSource()

previous_date_source: PreviousDateSource = PreviousDateSource()

speed_figures_source: SpeedFiguresSource = SpeedFiguresSource()

draw_bias_source: DrawBiasSource = DrawBiasSource()

has_fallen_source: HasFallenSource = HasFallenSource()


def get_feature_sources() -> List[FeatureSource]:
    return [
        horse_name_to_subject_id_source,

        win_probability_source, win_rate_source, show_rate_source,

        average_place_percentile_source,
        average_relative_distance_behind_source,

        purse_rate_source, percentage_beaten_source, scratched_rate_source,

        life_time_start_count_source, life_time_win_count_source, life_time_place_count_source,

        max_win_prob_source,

        previous_jockey_source,
        previous_win_prob_source,
        previous_place_percentile_source, previous_relative_distance_behind_source,

        previous_distance_source, previous_race_going_source, previous_race_class_source,
        previous_trainer_source,

        previous_date_source,
        previous_track_name_source,

        equipment_already_worn_source,

        draw_bias_source,

        sire_siblings_place_percentile_source,
        dam_siblings_place_percentile_source,
        sire_and_dam_siblings_place_percentile_source,
        dam_sire_siblings_place_percentile_source,

        # speed_figures_source,
        # has_fallen_source,
    ]
