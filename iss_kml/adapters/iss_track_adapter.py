from iss_kml.adapters.basic_sqlite_adapter import BasicSQLiteAdapter
from iss_kml.domain.iss_track.iss_track import IssTrack


class IssTrackAdapter(BasicSQLiteAdapter):
    def __init__(self, db_path, logger=None):
        super().__init__(database=db_path,
                         adapted_class=IssTrack,
                         logger=logger)
