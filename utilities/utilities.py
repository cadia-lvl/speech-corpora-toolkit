def seconds_to_hours_mins(seconds):
    mins = int((seconds / 60) % 60)
    hours = int(seconds / 60 / 60)
    return hours, mins
