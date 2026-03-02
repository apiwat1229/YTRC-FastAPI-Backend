from datetime import datetime


def format_date(value: datetime) -> str:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day = str(value.day).zfill(2)
    month = months[value.month - 1]
    year = value.year
    hour = str(value.hour).zfill(2)
    minute = str(value.minute).zfill(2)
    second = str(value.second).zfill(2)
    return f"{day}-{month}-{year} เวลา {hour} Hour {minute} : Minute : {second} Second"


def format_duration(seconds: float) -> str:
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours} Hour {minutes} : Minute : {secs} Second"
