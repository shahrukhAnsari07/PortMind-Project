def format_minutes(minutes: float) -> str:
    minutes = max(0, int(round(minutes)))

    hours = minutes // 60
    remaining = minutes % 60

    if hours == 0:
        return f"{remaining} min"

    if remaining == 0:
        return f"{hours} hr"

    return f"{hours} hr {remaining} min"


def minutes_to_clock(minutes: float) -> str:
    minutes = max(0, int(minutes))

    hours = (minutes // 60) % 24
    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"