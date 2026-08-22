from datetime import date


from app.utils.date_helpers import convert_to_mins, get_date_chunks, merge_date_chunks, compute_date_chunks, compute_weekend_dates



def test_convert_to_mins():

    assert convert_to_mins('0:40') == 40
    assert convert_to_mins('1:00') == 60
    assert convert_to_mins('2:13') == 133


def test_get_date_chunks():
    date_from = date(2026, 6, 20)
    date_to = date(2026, 7, 2)

    result = get_date_chunks(date_from, date_to)

    assert len(result) == 3
    assert result[0] == date(2026, 6, 22)
    assert result[1] == date(2026, 6, 27)
    assert result[2] == date(2026, 7, 2)


def test_merge_date_chunks():
    dep_chunk = [date(2026, 6, 22), date(2026, 6, 27)]
    arr_chunk = [date(2026, 8, 10), date(2026, 8, 15), date(2026, 8, 20)]

    result = merge_date_chunks(dep_chunk, arr_chunk)

    assert len(result) == 3
    assert result[0] == (date(2026, 6, 22), date(2026, 8, 10))
    assert result[1] == (date(2026, 6, 27), date(2026, 8, 15))
    assert result[2] == (date(2026, 6, 27), date(2026, 8, 20))


def test_compute_date_chunks():
    dep_start_date = date(2026, 4, 1)
    dep_end_date = date(2026, 4, 30)

    arr_start_date = date(2026, 4, 15) 
    arr_end_date = date(2026, 5, 15)

    result = compute_date_chunks(dep_start_date, dep_end_date, arr_start_date, arr_end_date)

    assert len(result) == 7
    assert result[0] == (date(2026, 4, 3), date(2026, 4, 17))
    assert result[1] == (date(2026, 4, 8), date(2026, 4, 22))
    assert result[2] == (date(2026, 4, 13), date(2026, 4, 27))
    assert result[3] == (date(2026, 4, 18), date(2026, 5, 2))
    assert result[4] == (date(2026, 4, 23), date(2026, 5, 7))
    assert result[5] == (date(2026, 4, 28), date(2026, 5, 12))
    assert result[6] == (date(2026, 4, 28), date(2026, 5, 17))


def test_compute_weekend_dates():
    date_from = date(2026, 7, 31)
    date_to = date(2026, 8, 15)

    result = compute_weekend_dates(date_from, date_to)

    assert len(result) == 3
    assert result[0] == (date(2026, 7, 31), date(2026, 7, 31))
    assert result[1] == (date(2026, 8, 7), date(2026, 8, 7))
    assert result[2] == (date(2026, 8, 14), date(2026, 8, 14))
