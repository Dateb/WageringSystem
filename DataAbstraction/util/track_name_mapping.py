def get_unique_track_name(track_name: str) -> str:
    if "Wolverhampton" in track_name:
        track_name = "Wolverhampton"
    if "Chelmsford" in track_name:
        track_name = "Chelmsford"
    if "Bangor" in track_name:
        track_name = "Bangor"
    if "Ascot" in track_name:
        track_name = "Ascot"
    if "Goodwood" in track_name:
        track_name = "Goodwood"

    if "PMU" in track_name:
        track_name = track_name[:-4]

    return track_name
