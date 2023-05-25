from iss_kml.domain.basic_domain.util import generic_serialize_roundtrip_test
from iss_kml.domain.iss_track.iss_track import IssPos, IssTrack


def test_iss_pos():
    iss_pos = IssPos(1, 2, 3, 4, 5, 1684980256)
    generic_serialize_roundtrip_test(IssPos, iss_pos)


def test_iss_track():
    iss_pos = IssPos(1, 2, 3, 4, 5, 1684980256)
    iss_track = IssTrack([iss_pos])
    generic_serialize_roundtrip_test(IssTrack, iss_track)
