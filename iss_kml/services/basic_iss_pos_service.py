from abc import ABC, abstractmethod


class IssPos:
    def __init__(self,
                 latitude: float,
                 longitude: float,
                 altitude: float,
                 speed: float,
                 footprint: float,
                 timestamp: int):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.speed = speed
        self.footprint = footprint
        self.timestamp = timestamp


class BasicIssPosService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_pos(self) -> IssPos:
        raise NotImplementedError
