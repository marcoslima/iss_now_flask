from functools import lru_cache

from latloncalc.latlon import LatLon


@lru_cache(maxsize=1)
def get_kml_template():
    with open('assets/iss_kml_template.kml', 'r') as f:
        kml = f.read()

    return kml


def get_footprint_coordinates(lat, lon, footprint):
    num_points = 128
    step = 360 / num_points
    coordinates = ''
    center = LatLon(lat, lon)
    for i in range(num_points + 1):
        angle = step * i
        p = center.offset(angle, footprint / 2, ellipse='sphere')
        coordinates += f'{p.lon},{p.lat},0 '

    return coordinates


def get_iss_kml(lat, lon, alt, footprint):
    kml = get_kml_template()
    coordinates = get_footprint_coordinates(lat, lon, footprint)
    return kml.format(latitude=lat,
                      longitude=lon,
                      altitude=alt,
                      footprint=coordinates)
