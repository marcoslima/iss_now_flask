from flask import Flask, request, Response
import requests

from iss_kml import get_iss_kml

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def get_iss_pos():
    # response = requests.get('http://api.open-notify.org/iss-now.json')
    # {
    #   "timestamp": 1684857759,
    #   "message": "success",
    #   "iss_position":
    #   {
    #       "longitude": "-161.7317",
    #       "latitude": "-43.9940"
    #   }
    # }
    response = requests.get('https://api.wheretheiss.at/v1/satellites/25544')
    data = response.json()
    return data['longitude'], data['latitude'], data['altitude']*1000


@app.route('/iss')
def iss():
    # params = request.args
    # bbox = params['BBOX']
    # bbox = bbox.split(',')
    # west = float(bbox[0])
    # south = float(bbox[1])
    # east = float(bbox[2])
    # north = float(bbox[3])
    #
    # center_lng = ((east - west) / 3) + west
    # center_lat = ((north - south) / 3) + south
    long, lat, alt = get_iss_pos()

    kml = get_iss_kml(lat, long, alt)

    return Response(kml, content_type='application/vnd.google-earth.kml+xml')


if __name__ == '__main__':
    app.run()
