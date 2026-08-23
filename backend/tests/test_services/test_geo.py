import pytest
from unittest.mock import AsyncMock, MagicMock


from app.services.geo import check_country_reality, check_airports_reality, compute_country_airports, get_nearby_airports, compute_nearby_airports
from app.services.exceptions import AirportNotFoundError



@pytest.mark.asyncio
async def test_check_country_reality_success():
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars().first.return_value = "SomePolishAirport"
    mock_session.execute.return_value = mock_result

    await check_country_reality(mock_session, "PL")


@pytest.mark.asyncio
async def test_check_country_reality_failure():
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars().first.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Provided country code does not exist or has no airports"):
            await check_country_reality(mock_session, "XYZ")


@pytest.mark.asyncio
async def test_check_airports_reality_success():
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = ["WRO", "KRK", "POZ"]
    mock_session.execute.return_value = mock_result

    await check_airports_reality(mock_session, ["WRO", "KRK", "POZ"])


@pytest.mark.asyncio
async def test_check_airports_reality_failure():
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = ["WRO", "KRK", "GDN"]
    mock_session.execute.return_value = mock_result

    with pytest.raises(AirportNotFoundError, match="POZ"):
        await check_airports_reality(mock_session, ["WRO", "KRK", "POZ"])


@pytest.mark.asyncio
async def test_compute_country_airports_success():
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = ["WRO", "KRK", "GDN"]
    mock_session.execute.return_value = mock_result

    result = await compute_country_airports(mock_session, "PL")
    assert result == ["WRO", "KRK", "GDN"]


@pytest.mark.asyncio
async def test_compute_country_airports_failure():
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = []
    mock_session.execute.return_value = mock_result

    with pytest.raises(ValueError, match="No airports found for the provided country code"):
        await compute_country_airports(mock_session, "XYZ")


@pytest.mark.asyncio
async def test_get_nearby_airports_success():
    mock_session = AsyncMock()

    nearby_result = MagicMock()
    nearby_result.all.return_value = ["WRO", "POZ"]
    mock_session.scalars.return_value = nearby_result

    result = await get_nearby_airports(mock_session, "KRK", 200)

    assert result == ["WRO", "POZ"]
    mock_session.scalar.assert_not_awaited()
    mock_session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_nearby_airports_origin_not_found():
    mock_session = AsyncMock()
    nearby_result = MagicMock()
    nearby_result.all.return_value = []
    mock_session.scalars.return_value = nearby_result

    result = await get_nearby_airports(mock_session, "XYZ", 200)

    assert result == []
    mock_session.scalar.assert_not_awaited()
    mock_session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_nearby_airports_no_nearby_airports():
    mock_session = AsyncMock()

    nearby_result = MagicMock()
    nearby_result.all.return_value = []
    mock_session.scalars.return_value = nearby_result

    result = await get_nearby_airports(mock_session, "KRK", 200)

    assert result == []
    mock_session.scalar.assert_not_awaited()
    mock_session.scalars.assert_awaited_once()


@pytest.mark.asyncio
async def test_compute_nearby_airports_success():
    mock_session = AsyncMock()

    nearby_result = MagicMock()
    nearby_result.all.return_value = ["WRO", "POZ"]
    mock_session.scalars.return_value = nearby_result

    result = await compute_nearby_airports(mock_session, ["KRK"], 200)

    assert result == ["WRO", "POZ"]
    mock_session.scalar.assert_not_awaited()
    mock_session.scalars.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "airports_iata, max_radius",
    [
        (None, 200),
        ([], 200),
        (["WRO", "KRK"], 200),
        (["WRO"], None)
    ],
)
async def test_compute_nearby_airports_invalid_params(airports_iata, max_radius):
    mock_session = AsyncMock()

    result = await compute_nearby_airports(mock_session, airports_iata, max_radius)

    assert result == []
    mock_session.scalar.assert_not_awaited()
    mock_session.scalars.assert_not_awaited()
