from SampleExtraction.feature_sources.feature_sources import PreviousValueSource

previous_value_source: PreviousValueSource = PreviousValueSource()

# horse_name_to_subject_id_source: HorseNameToSubjectIdSource = HorseNameToSubjectIdSource()
#
# win_rate_source: WinRateSource = WinRateSource()
#
# average_win_probability_source:  AverageWinProbabilitySource = AverageWinProbabilitySource()
#
# average_place_percentile_source: AveragePlacePercentileSource = AveragePlacePercentileSource()
# average_place_percentile_source.average_attribute_groups.append(["name"])
#
# average_momentum_source: AverageMomentumSource = AverageMomentumSource()
#
# sire_siblings_momentum_source: AverageMomentumSource = AverageMomentumSource()
# sire_siblings_momentum_source.average_attribute_groups.append(["sire", "age"])
#
# dam_siblings_momentum_source: AverageMomentumSource = AverageMomentumSource()
# dam_siblings_momentum_source.average_attribute_groups.append(["dam", "age"])
#
# sire_and_dam_siblings_momentum_source: AverageMomentumSource = AverageMomentumSource()
# sire_and_dam_siblings_momentum_source.average_attribute_groups.append(["sire", "dam", "age"])
#
# dam_sire_siblings_momentum_source: AverageMomentumSource = AverageMomentumSource()
# dam_sire_siblings_momentum_source.average_attribute_groups.append(["dam_sire", "age"])
#
# average_relative_distance_behind_source: AverageRelativeDistanceBehindSource = AverageRelativeDistanceBehindSource()
# average_relative_distance_behind_source.average_attribute_groups.append(["name"])
#
# show_rate_source: ShowRateSource = ShowRateSource()
#
# purse_rate_source: PurseRateSource = PurseRateSource()
#
# dam_and_sire_average_momentum_source: AverageMomentumSource = AverageMomentumSource()
#
# scratched_rate_source: ScratchedRateSource = ScratchedRateSource()
# pulled_up_rate_source: PulledUpRateSource = PulledUpRateSource()
#
# life_time_start_count_source: LifeTimeStartCountSource = LifeTimeStartCountSource()
# life_time_win_count_source: LifeTimeWinCountSource = LifeTimeWinCountSource()
# life_time_place_count_source: LifeTimePlaceCountSource = LifeTimePlaceCountSource()

#Max based sources:
# max_win_prob_source: MaxWinProbabilitySource = MaxWinProbabilitySource()

#Previous value based sources:
# previous_jockey_source: PreviousJockeySource = PreviousJockeySource()
# previous_trainer_source: PreviousTrainerSource = PreviousTrainerSource()
# previous_owner_source: PreviousOwnerSource = PreviousOwnerSource()
#
# previous_momentum_source = PreviousMomentumSource()
# previous_place_percentile_source: PreviousPlacePercentileSource = PreviousPlacePercentileSource()
# previous_relative_distance_behind_source: PreviousRelativeDistanceBehindSource = PreviousRelativeDistanceBehindSource()
# previous_track_name_source: PreviousTrackNameSource = PreviousTrackNameSource()
#
# previous_distance_source: PreviousDistanceSource = PreviousDistanceSource()
# previous_race_going_source: PreviousRaceGoingSource = PreviousRaceGoingSource()
# previous_race_class_source: PreviousRaceClassSource = PreviousRaceClassSource()
#
# previous_pulled_up_source: PreviousPulledUpSource = PreviousPulledUpSource()
#
# equipment_already_worn_source: EquipmentAlreadyWornSource = EquipmentAlreadyWornSource()
#
# previous_date_source: PreviousDateSource = PreviousDateSource()
#
# draw_bias_source: DrawBiasSource = DrawBiasSource()
#
# best_class_place_source: BestClassPlaceSource = BestClassPlaceSource()
#
# window_time_length_source: WindowTimeLengthSource = WindowTimeLengthSource(window_size=7)
#
# track_variant_source: TrackVariantSource = TrackVariantSource()


FEATURE_SOURCES = [
    previous_value_source
    ]
