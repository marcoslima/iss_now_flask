from unittest.mock import patch, MagicMock

from iss_kml.interactors import IssInteractor
from iss_kml.services.basic_iss_pos_service import IssPos


@patch.object(IssInteractor, '_get_footprint_coordinates')
@patch.object(IssInteractor, '_make_kml')
def test_iss_interactor(mock_make_kml, mock_get_footprint_coordinates):
    mock_iss_pos_service = MagicMock()
    kml_template = MagicMock()
    iss_interactor = IssInteractor(
        iss_pos_service_instance=mock_iss_pos_service,
        kml_template=kml_template)

    result = iss_interactor.run()

    mock_iss_pos_service.get_pos.assert_called_once()
    mock_pos = mock_iss_pos_service.get_pos.return_value
    mock_get_footprint_coordinates.assert_called_once_with(mock_pos)
    mock_coordinates = mock_get_footprint_coordinates.return_value
    mock_make_kml.assert_called_once_with(mock_pos, mock_coordinates)

    assert result == mock_make_kml.return_value


def test_make_kml():
    mock_kml_template = MagicMock()
    iss_interactor = IssInteractor(iss_pos_service_instance=None,
                                   kml_template=mock_kml_template)
    mock_iss_pos = MagicMock()
    mock_coordinates = MagicMock()

    result = iss_interactor._make_kml(mock_iss_pos, mock_coordinates)

    mock_kml_template.format.assert_called_once_with(
        latitude=mock_iss_pos.latitude,
        longitude=mock_iss_pos.longitude,
        altitude=mock_iss_pos.altitude,
        footprint=mock_coordinates)

    assert result == mock_kml_template.format.return_value


def test_get_footprint_coordinates():
    mock_iss_pos = IssPos(latitude=1,
                          longitude=2,
                          altitude=3,
                          footprint=2,
                          speed=5,
                          timestamp=6)

    result = IssInteractor._get_footprint_coordinates(mock_iss_pos, 4)

    # !assert do tipo "snapshot"
    assert result == '2.0,1.0089932202939478,0 ' \
                     '2.0089945902135753,0.9999999876803236,0 ' \
                     '2.0,0.991006779706052,0 ' \
                     '1.9910054097864247,0.9999999876803236,0 ' \
                     '2.0,1.0089932202939478,0 '
