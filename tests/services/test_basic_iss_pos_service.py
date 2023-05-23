from iss_kml.services.basic_iss_pos_service import BasicIssPosService


def test_basic_iss_pos_service():
    class ImplementService(BasicIssPosService):
        def get_pos(self):
            return 42
    iss_pos_service = ImplementService()
    result = iss_pos_service.get_pos()
    assert result == 42
