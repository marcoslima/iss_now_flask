import requests

from iss_kml.domain import ApiData
from iss_kml.services.basic_iss_pos_service import BasicIssPosService, IssPos


class WhereTheIssAt(BasicIssPosService):
    API_URL = 'https://api.wheretheiss.at/v1/satellites/25544'

    def get_pos(self) -> IssPos:
        response = requests.get(self.API_URL, timeout=5).json()
        api_data = ApiData.parse_obj(response)
        return IssPos(latitude=api_data.latitude,
                      longitude=api_data.longitude,
                      altitude=api_data.altitude * 1000,
                      speed=api_data.velocity,
                      footprint=api_data.footprint,
                      timestamp=api_data.timestamp)
