from flask import Flask, send_from_directory, json
from os.path import exists
import os
import requests

app = Flask(__name__)


@app.route("/")
def serve_index():
    return send_from_directory('frontend', "index.html")

last_rover_coords = [0, 0]
def update_rover_coords(lat_lng_array):
    last_rover_coords = lat_lng_array


@app.route("/tile/<z>/<x>/<y>")
def serve_tile(z, x, y):
    tileFilePath = os.path.dirname(os.path.abspath(__file__)) + "/tiles/z{},x{},y{}.jpg".format(z,x,y)
    if exists(tileFilePath):
        tileFD = open(tileFilePath, "rb")
        img = tileFD.read()
        tileFD.close()
        return img
        
    if not os.getenv("NO_NETWORK_TILE_REQUESTS"):
        tileRequest = requests.get("https://api.maptiler.com/tiles/satellite-v2/{}/{}/{}.jpg?key=zlVsrqByDUUiajrK53SU".format(z, x, y))
        tileFile = open(tileFilePath, "wb+")
        print("Successfully got tile from network")
        tileFile.write(tileRequest.content)
        return tileRequest.content

    return None


@app.route("/roverCoords")
def return_rover_coords():
    return json.dumps(last_rover_coords)

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory('frontend', path)

def start_map_server(debug=False):
    app.run(debug=debug, host='0.0.0.0', port="5000")
    

if __name__ == "__main__":
    start_map_server(debug=True)