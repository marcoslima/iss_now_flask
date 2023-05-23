from unittest.mock import patch

from iss_kml.services import WhereTheIssAt
from iss_kml.services.basic_iss_pos_service import IssPos


def prefixed(text):
    prefix = 'iss_kml.services.wheretheiss'
    return f'{prefix}.{text}'


@patch(prefixed('requests'))
@patch(prefixed('IssPos'), spec=IssPos)
@patch(prefixed('ApiData'), spec=True)
def test_where_the_iss_service(mock_api_data_cls, mock_iss_pos, mock_requests):
    iss_pos_service = WhereTheIssAt()

    result = iss_pos_service.get_pos()

    mock_requests.get.assert_called_once_with(WhereTheIssAt.API_URL, timeout=5)
    mock_response = mock_requests.get.return_value
    mock_response.json.assert_called_once_with()
    mock_json_data = mock_response.json.return_value
    mock_api_data_cls.parse_obj.assert_called_once_with(mock_json_data)
    mock_api_data = mock_api_data_cls.parse_obj.return_value
    mock_iss_pos.assert_called_once_with(
        latitude=mock_api_data.latitude,
        longitude=mock_api_data.longitude,
        altitude=mock_api_data.altitude * 1000,
        speed=mock_api_data.velocity,
        footprint=mock_api_data.footprint,
        timestamp=mock_api_data.timestamp
    )

    assert result == mock_iss_pos.return_value
