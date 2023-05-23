from iss_kml.domain import ApiData


def test_api_data():
    raw_json = {"name": "iss", "id": 25544, "latitude": 44.146685470113,
                "longitude": -17.183318738253, "altitude": 418.37462199472,
                "velocity": 27601.517994068, "visibility": "daylight",
                "footprint": 4499.185005727, "timestamp": 1684866114,
                "daynum": 2460088.2652083, "solar_lat": 20.635685129656,
                "solar_lon": 263.7187133765, "units": "kilometers"}
    api_data = ApiData.parse_obj(raw_json)
    assert api_data.name == "iss"
    assert api_data.id == 25544
    assert api_data.latitude == 44.146685470113
    assert api_data.longitude == -17.183318738253
    assert api_data.altitude == 418.37462199472
    assert api_data.velocity == 27601.517994068
    assert api_data.visibility == "daylight"
    assert api_data.footprint == 4499.185005727
    assert api_data.timestamp == 1684866114
    assert api_data.daynum == 2460088.2652083
    assert api_data.solar_lat == 20.635685129656
    assert api_data.solar_lon == 263.7187133765
    assert api_data.units == "kilometers"
