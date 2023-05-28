from datetime import datetime, timezone
from typing import List

from latloncalc.latlon import LatLon
from vector import Vector

from iss_kml.adapters.basic_persist_adapter import BasicPersistAdapter
from iss_kml.domain.iss_track.iss_track import IssTrack
from iss_kml.services.basic_iss_pos_service import BasicIssPosService, IssPos


class IssInteractor:
    LIMIT_TIMESTAMP = None
    PRINT_TIMESTAMP = True
    EQUALIZE_YT_DELAY = True

    def __init__(self,
                 iss_track_adapter: BasicPersistAdapter,
                 iss_pos_service_instance: BasicIssPosService,
                 kml_template: str
                 ):
        self.iss_track_adapter = iss_track_adapter
        self.iss_pos_service = iss_pos_service_instance
        self.kml_template = kml_template

    def run(self):
        try:
            iss_pos = self.iss_pos_service.get_pos()
            iss_track = self._get_current_track()
            self._update_iss_track(iss_track, iss_pos)
            self._print_timestamp(iss_pos)

            if self.EQUALIZE_YT_DELAY:
                self.LIMIT_TIMESTAMP = iss_pos.timestamp - 10

            if self.LIMIT_TIMESTAMP is not None:
                for i in range(len(iss_track.positions)):
                    if iss_track.positions[i].timestamp > self.LIMIT_TIMESTAMP:
                        iss_track.positions = iss_track.positions[:i]
                        iss_pos = iss_track.positions[-1]
                        break

            coordinates = self._get_footprint_coordinates(iss_pos)
            track = iss_track.get_track_coordinates_kml()
            yt_iss_live = self._get_yt_iss_live_coordinates(
                iss_track.positions[-2:])
            kml = self._make_kml(iss_pos, coordinates, track, yt_iss_live)
            return kml
        except Exception as e:
            print(f'Error: {e.__class__.__name__}: {e}')

    def _print_timestamp(self, iss_pos):
        if self.PRINT_TIMESTAMP:
            dtts = datetime.fromtimestamp(iss_pos.timestamp, tz=timezone.utc)
            print(f'Current position timestamp: {iss_pos.timestamp} - {dtts}')

    def _make_kml(self,
                  iss_pos: IssPos,
                  coordinates: str,
                  track: str,
                  yt_iss_live: str):
        return self.kml_template.format(latitude=iss_pos.latitude,
                                        longitude=iss_pos.longitude,
                                        altitude=iss_pos.altitude,
                                        footprint=coordinates,
                                        track=track,
                                        yt_iss_live=yt_iss_live)

    @staticmethod
    def _get_footprint_coordinates(iss_pos: IssPos, num_points=128):
        step = 360 / num_points
        coordinates = ''
        center = LatLon(iss_pos.latitude, iss_pos.longitude)
        radius = iss_pos.footprint / 2
        for i in range(num_points + 1):
            angle = step * i
            p = center.offset(angle, radius, ellipse='sphere')
            coordinates += f'{p.lon},{p.lat},0 '

        return coordinates

    @staticmethod
    def _update_iss_track(iss_track, iss_pos):
        iss_track.positions.append(iss_pos)
        iss_track.save()

    def _get_current_track(self) -> IssTrack:
        iss_track = self.iss_track_adapter.get_by_id('1')
        if iss_track is None:
            iss_track = IssTrack(entity_id='1', positions=[])
            iss_track.set_adapter(self.iss_track_adapter)
            iss_track.save()

        return iss_track

    @staticmethod
    def _get_yt_iss_live_coordinates(iss_pos: List[IssPos]):
        class Point:
            def __init__(self, longitude, latitude):
                self.longitude = longitude
                self.latitude = latitude

            def __repr__(self):
                return f'{self.longitude},{self.latitude},0 '

        width = 2.5
        height = 1.4
        pos0 = Vector(iss_pos[0].longitude, iss_pos[0].latitude)
        pos1 = Vector(iss_pos[1].longitude, iss_pos[1].latitude)

        base_vector = (pos1 - pos0) * (1.0 / (pos1 - pos0).norm)
        # bv.x * ov.x + bv.y * ov.y = 0
        # ov.x = -bv.y
        # ov.y = bv.x
        ortho_vector = Vector(-base_vector.values[1], base_vector.values[0])
        ortho_vector *= 1.0 / ortho_vector.norm

        tl = pos1 - (base_vector * (width / 2)) - (ortho_vector * (height / 2))
        tr = tl + base_vector * width
        br = tr + ortho_vector * height
        bl = br - base_vector * width
        return f'{Point(*tl.values)}' \
               f'{Point(*tr.values)}' \
               f'{Point(*br.values)}' \
               f'{Point(*bl.values)}' \
               f'{Point(*tl.values)}'
