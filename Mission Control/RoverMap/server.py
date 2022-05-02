from nis import maps
from traceback import print_tb
from flask import Flask, send_from_directory, json, Response
from os.path import exists
import os
import threading



class MapServer:

    app = Flask(__name__)
    last_rover_coords = [-1, 0]
    
    def register_routes(self):
        @self.app.route("/")
        def serve_index():
            return send_from_directory('frontend', "index.html")

        @self.app.route("/tile/<z>/<x>/<y>")
        def serve_tile(z, x, y):
            tileFilePath = os.path.dirname(os.path.abspath(__file__)) + "/tiles/z{}, x{}, y{}.jpg".format(z,x,y)
            if exists(tileFilePath):
                tileFD = open(tileFilePath, "rb")
                img = tileFD.read()
                tileFD.close()
                return img

            return Response(status=404)


        @self.app.route("/roverCoords")
        def return_rover_coords():
            print(f"lastcoords {self.last_rover_coords}")
            return json.dumps(self.last_rover_coords)

        @self.app.route("/<path:path>")
        def serve_static(path):
            return send_from_directory('frontend', path)

    
    def update_rover_coords(self, lat_lng_array):
        print("updating rover coords")
        self.last_rover_coords = lat_lng_array
        print(f"updated {self.last_rover_coords}")

    def start(self):
        print("starting server")

        def thread_target():
            self.app.run(debug=False, host='0.0.0.0', port="5000")
        
        threading.Thread(target=thread_target).start()


if __name__ == "__main__":
    mapServer = MapServer()
    mapServer.register_routes()
    mapServer.start()