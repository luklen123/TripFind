from datetime import timedelta, date



def merge_date_chunks(dep_chunk: list[date], arr_chunk: list[date]) -> list[tuple[date, date]]:
    chunks = []
    max_len = max(len(dep_chunk), len(arr_chunk))

    for i in range(max_len):
        dep = dep_chunk[i] if i < len(dep_chunk) else dep_chunk[-1]
        arr = arr_chunk[i] if i < len(arr_chunk) else arr_chunk[-1]

        if arr < dep:
            chunks.append((arr, arr))
        else:
            chunks.append((dep, arr))

    return chunks


def get_date_chunks(date_from: date, date_to: date, window_days: int = 7) -> list[date]:
    date_chunks = []

    current_date = date_from 
    while current_date <= date_to:
        date_chunks.append(current_date)
        current_date += timedelta(days=window_days)

    return date_chunks


def compute_date_chunks(dep_date_start: date, dep_date_end: date, arr_date_start: date, arr_date_end: date) -> list[tuple[date, date]]:
    dep_date_chunks = get_date_chunks(dep_date_start, dep_date_end)
    arr_date_chunks = get_date_chunks(arr_date_start, arr_date_end)

    return merge_date_chunks(dep_date_chunks, arr_date_chunks)


def convert_to_mins(duration: str) -> int:
    hours, minutes = duration.split(':')

    return (int(hours) * 60 + int(minutes))


def compute_weekend_dates(date_from: date, date_to: date) -> list[tuple[date, date]]:
    weekend_dates = []

    # 0 - Monday, ... , 6 - Sunday
    if date_from.weekday() >= 4:
        weekend_dates.append((date_from, date_from))
    else:
        temp_date = date_from + timedelta(days=(4 - date_from.weekday()))
        weekend_dates.append((temp_date, temp_date))

    to_add = 6 - date_from.weekday() + 5
    current_date = date_from + timedelta(days=to_add)

    while current_date <= date_to:
        weekend_dates.append((current_date, current_date))
        current_date += timedelta(days=7)

    return weekend_dates