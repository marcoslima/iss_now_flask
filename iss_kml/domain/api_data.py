from pydantic import BaseModel


class ApiData(BaseModel):
    name: str
    id: int
    latitude: float
    longitude: float
    altitude: float
    velocity: float
    visibility: str
    footprint: float
    timestamp: int
    daynum: float
    solar_lat: float
    solar_lon: float
    units: str
