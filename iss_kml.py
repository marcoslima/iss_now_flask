from functools import lru_cache


@lru_cache(maxsize=1)
def get_kml_template():
    with open('assets/iss_kml_template.kml', 'r') as f:
        kml = f.read()

    return kml


def get_iss_kml(lat, lon, alt):
    kml = get_kml_template()
    return kml.format(latitude=lat, longitude=lon, altitude=alt)
