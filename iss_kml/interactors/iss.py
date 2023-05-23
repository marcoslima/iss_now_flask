from latloncalc.latlon import LatLon

from iss_kml.services.basic_iss_pos_service import BasicIssPosService, IssPos


class IssInteractor:
    def __init__(self,
                 iss_pos_service_instance: BasicIssPosService,
                 kml_template: str
                 ):
        self.iss_pos_service = iss_pos_service_instance
        self.kml_template = kml_template

    def run(self):
        iss_pos = self.iss_pos_service.get_pos()
        coordinates = self._get_footprint_coordinates(iss_pos)
        kml = self._make_kml(iss_pos, coordinates)
        return kml

    def _make_kml(self, iss_pos: IssPos, coordinates: str):
        return self.kml_template.format(latitude=iss_pos.latitude,
                                        longitude=iss_pos.longitude,
                                        altitude=iss_pos.altitude,
                                        footprint=coordinates)

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
