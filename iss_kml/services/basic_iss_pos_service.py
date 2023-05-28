from abc import ABC, abstractmethod
from marshmallow import fields, post_load

from iss_kml.domain.basic_domain import BasicValue


class IssPos(BasicValue):
    def __init__(self,
                 latitude: float,
                 longitude: float,
                 altitude: float,
                 speed: float,
                 footprint: float,
                 timestamp: int):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.speed = speed
        self.footprint = footprint
        self.timestamp = timestamp

    class Schema(BasicValue.Schema):
        latitude = fields.Float(required=True, allow_none=False)
        longitude = fields.Float(required=True, allow_none=False)
        altitude = fields.Float(required=True, allow_none=False)
        speed = fields.Float(required=True, allow_none=False)
        footprint = fields.Float(required=True, allow_none=False)
        timestamp = fields.Integer(required=True, allow_none=False)

        @post_load
        def on_load(self, data, **_kwargs):
            return IssPos(**data)


class BasicIssPosService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_pos(self) -> IssPos:
        raise NotImplementedError
