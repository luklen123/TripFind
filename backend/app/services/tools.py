from datetime import date, timedelta



def get_date_chunks(date_from: date, date_to: date, window_days: int = 7):
    current_date = date_from 
    while current_date <= date_to:
        yield current_date
        current_date += timedelta(days=window_days)


def convert_to_mins(duration: str) -> int:
    hours, minutes = duration.split(':')

    return (hours * 60 + minutes)



