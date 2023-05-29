from datetime import datetime, timezone
from math import acos, pi
from typing import List

from latloncalc.latlon import LatLon
from vector import Vector

from iss_kml.adapters.basic_persist_adapter import BasicPersistAdapter
from iss_kml.domain.iss_track.iss_track import IssTrack
from iss_kml.services.basic_iss_pos_service import BasicIssPosService, IssPos


class IssInteractor:
    LIMIT_TIMESTAMP = None
    PRINT_TIMESTAMP = False
    YT_TIME_OFFSET_SECONDS = 0

    def __init__(self,
                 iss_track_adapter: BasicPersistAdapter,
                 iss_pos_service_instance: BasicIssPosService,
                 kml_template: str
                 ):
        self.iss_track_adapter = iss_track_adapter
        self.iss_pos_service = iss_pos_service_instance
        self.kml_template = kml_template

    @staticmethod
    def _get_track_until_timestamp(iss_track, timestamp):
        size = len(iss_track.positions)
        for i in range(size):
            current_pos = iss_track.positions[size - 1 - i]
            if current_pos.timestamp < timestamp:
                return iss_track.positions[:size - i]

    def run(self):
        try:
            iss_pos = self.iss_pos_service.get_pos()
            iss_track = self._get_current_track()
            self._update_iss_track(iss_track, iss_pos)
            self._print_timestamp(iss_pos)

            if self.LIMIT_TIMESTAMP is not None:
                positions = self._get_track_until_timestamp(
                    iss_track, self.LIMIT_TIMESTAMP)
                iss_track.positions = positions
                iss_pos = iss_track.positions[-1]

            coordinates = self._get_footprint_coordinates(iss_pos)
            track = iss_track.get_track_coordinates_kml(2000)
            yt_iss_live = self._get_yt_iss_live_coordinates(iss_track)
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
    def _get_yt_iss_live_coordinates(iss_track: IssTrack):
        """
        Footprint do iss live em https://youtu.be/itdpuGHAcpg
        :param iss_track:
        :return: coordenadas representando o footprint do iss live no formato
        longitude,latitude,0 (KML)
        """
        class Point:
            def __init__(self, longitude, latitude):
                self.longitude = longitude
                self.latitude = latitude

            def __repr__(self):
                return f'{self.longitude},{self.latitude},0 '

        last_timestamp = iss_track.positions[-1].timestamp
        delayed_last = last_timestamp + IssInteractor.YT_TIME_OFFSET_SECONDS
        iss_pos = IssInteractor._get_track_until_timestamp(iss_track,
                                                           delayed_last)[-2:]
        width = 250
        height = 140
        p1 = LatLon(iss_pos[0].latitude, iss_pos[0].longitude)
        p2 = LatLon(iss_pos[1].latitude, iss_pos[1].longitude)
        heading = p1.heading_initial(p2)
        angle = heading
        center = p1
        angle -= 180
        ml = center.offset(angle, width / 2, ellipse='sphere')
        angle += 90
        tl = ml.offset(angle, height / 2, ellipse='sphere')
        angle += 90
        tr = tl.offset(angle, width, ellipse='sphere')
        angle += 90
        br = tr.offset(angle, height, ellipse='sphere')
        angle += 90
        bl = br.offset(angle, width, ellipse='sphere')
        return f'{Point(tl.lon, tl.lat)}' \
               f'{Point(tr.lon, tr.lat)}' \
               f'{Point(br.lon, br.lat)}' \
               f'{Point(bl.lon, bl.lat)}' \
               f'{Point(tl.lon, tl.lat)}'


def angle_c(angle):
    if angle < 0:
        return angle + 360
    if angle > 360:
        return angle - 360
    return angle
