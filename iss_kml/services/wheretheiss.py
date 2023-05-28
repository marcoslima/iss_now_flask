import requests

from iss_kml.domain import ApiData
from iss_kml.services.basic_iss_pos_service import BasicIssPosService, IssPos
import json


class WhereTheIssAt(BasicIssPosService):
    API_URL = 'https://api.wheretheiss.at/v1/satellites/25544'
    READ_FROM_SERVICE = True

    def get_pos(self) -> IssPos:
        if self.READ_FROM_SERVICE:
            position = self._get_pos_from_service()
            self._write_position(position)
        else:
            position = self._get_pos_from_file()

        return position

    @staticmethod
    def _write_position(position):
        with open('/tmp/iss_last_position.json', 'w') as f:
            json.dump(position.to_json(), f)

    def _get_pos_from_service(self):
        try:
            response = requests.get(self.API_URL, timeout=5).json()
        except requests.exceptions.ConnectTimeout:
            return self._get_pos_from_file()

        api_data = ApiData.parse_obj(response)
        position = IssPos(latitude=api_data.latitude,
                          longitude=api_data.longitude,
                          altitude=api_data.altitude * 1000,
                          speed=api_data.velocity,
                          footprint=api_data.footprint,
                          timestamp=api_data.timestamp)
        return position

    @staticmethod
    def _get_pos_from_file():
        with open('/tmp/iss_last_position.json', 'r') as f:
            return IssPos.from_json(json.load(f))
