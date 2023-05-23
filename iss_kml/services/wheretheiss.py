import requests

from iss_kml.services.basic_iss_pos_service import BasicIssPosService, IssPos


class WhereTheIssAt(BasicIssPosService):
    API_URL = 'https://api.wheretheiss.at/v1/satellites/25544'

    def get_pos(self) -> IssPos:
        response = requests.get(self.API_URL, timeout=5).json()
        return IssPos(latitude=response['latitude'],
                      longitude=response['longitude'],
                      altitude=response['altitude']*1000,
                      speed=response['velocity'],
                      footprint=response['footprint'],
                      timestamp=response['timestamp'])
