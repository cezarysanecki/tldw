def timestamp_to_seconds(timestamp: str) -> float:
    """
    Convert WebVTT timestamp to seconds.

    Args:
        timestamp: WebVTT timestamp in format "HH:MM:SS.mmm"

    Returns:
        Float representing total seconds
    """
    time_parts = timestamp.split(':')
    hours = float(time_parts[0])
    minutes = float(time_parts[1])
    seconds = float(time_parts[2])

    return hours * 3600 + minutes * 60 + seconds


def ts_to_secs(timestamp):
    return timestamp.in_seconds() + (timestamp.milliseconds / 1000)


def seconds_to_timestamp(total_seconds: float) -> str:
    """
    Convert seconds to WebVTT timestamp.

    Args:
        total_seconds: Float representing total seconds

    Returns:
        WebVTT timestamp in format "HH:MM:SS.mmm"
    """
    hours = int(total_seconds // 3600)
    remaining = total_seconds % 3600
    minutes = int(remaining // 60)
    seconds = remaining % 60

    # Format with leading zeros and exactly 3 decimal places
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"