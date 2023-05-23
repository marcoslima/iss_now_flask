from functools import lru_cache

from flask import Flask, Response

from iss_kml.interactors import IssInteractor
from iss_kml.services import WhereTheIssAt

app = Flask(__name__)


@lru_cache(maxsize=1)
def get_kml_template():
    with open('templates/iss_kml_template.kml', 'r') as f:
        kml = f.read()

    return kml


@app.route('/iss')
def iss():
    kml_template = get_kml_template()
    iss_pos_service = WhereTheIssAt()
    interactor = IssInteractor(iss_pos_service, kml_template)
    kml = interactor.run()
    return Response(kml, content_type='application/vnd.google-earth.kml+xml')


if __name__ == '__main__':
    app.run()
