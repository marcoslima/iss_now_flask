from latloncalc.latlon import LatLon

from iss_kml.adapters.basic_persist_adapter import BasicPersistAdapter
from iss_kml.domain.iss_track.iss_track import IssTrack
from iss_kml.services.basic_iss_pos_service import BasicIssPosService, IssPos


class IssInteractor:
    def __init__(self,
                 iss_track_adapter: BasicPersistAdapter,
                 iss_pos_service_instance: BasicIssPosService,
                 kml_template: str
                 ):
        self.iss_track_adapter = iss_track_adapter
        self.iss_pos_service = iss_pos_service_instance
        self.kml_template = kml_template

    def run(self):
        iss_pos = self.iss_pos_service.get_pos()
        coordinates = self._get_footprint_coordinates(iss_pos)
        iss_track = self._get_current_track()
        self._update_iss_track(iss_track, iss_pos)
        track = iss_track.get_track_coordinates_kml()
        kml = self._make_kml(iss_pos, coordinates, track)
        return kml

    def _make_kml(self, iss_pos: IssPos, coordinates: str, track: str):
        return self.kml_template.format(latitude=iss_pos.latitude,
                                        longitude=iss_pos.longitude,
                                        altitude=iss_pos.altitude,
                                        footprint=coordinates,
                                        track=track)

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
