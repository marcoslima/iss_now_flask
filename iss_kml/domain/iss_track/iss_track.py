from dataclasses import dataclass
from typing import List

from marshmallow import fields, post_load

from iss_kml.domain.basic_domain import BasicEntity, BasicValue


@dataclass
class IssPos(BasicValue):
    latitude: float
    longitude: float
    altitude: float
    speed: float
    footprint: float
    timestamp: int

    class Schema(BasicValue.Schema):
        latitude = fields.Float()
        longitude = fields.Float()
        altitude = fields.Float()
        speed = fields.Float()
        footprint = fields.Float()
        timestamp = fields.Int()

        @post_load
        def on_load(self, data, **_kwargs):
            return IssPos(**data)


class IssTrack(BasicEntity):
    def __init__(self,
                 positions: List[IssPos],
                 entity_id=None):
        super().__init__(entity_id)
        self.positions = positions

    def get_track_coordinates_kml(self, max_points=None):
        coordinates = ''
        if max_points is None:
            max_points = len(self.positions)
        for pos in self.positions[-max_points:]:
            coordinates += f'{pos.longitude},{pos.latitude},{pos.altitude} '

        return coordinates

    class Schema(BasicEntity.Schema):
        positions = fields.List(fields.Nested(IssPos.Schema),
                                required=True,
                                allow_none=False)

        @post_load
        def on_load(self, data, **_kwargs):
            return IssTrack(**data)
