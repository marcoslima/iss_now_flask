from functools import lru_cache
from math import pi, cos, sin


@lru_cache(maxsize=1)
def get_kml_template():
    with open('assets/iss_kml_template.kml', 'r') as f:
        kml = f.read()

    return kml


def convert_meters_to_latlon(meters):
    return meters / 111111


def get_footprint_coordinates(lat, lon, footprint):
    radius = convert_meters_to_latlon(1000 * footprint / 2)
    num_points = 128
    step = pi * 2 / num_points
    coordinates = ''
    for i in range(num_points):
        angle = step * i
        x = radius * cos(angle)
        y = radius * sin(angle)
        coordinates += f'{lon + x},{lat + y},0 '

    return coordinates


def get_iss_kml(lat, lon, alt, footprint):
    kml = get_kml_template()
    coordinates = get_footprint_coordinates(lat, lon, footprint)
    return kml.format(latitude=lat,
                      longitude=lon,
                      altitude=alt,
                      footprint=coordinates)
