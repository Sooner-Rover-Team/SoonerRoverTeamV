import zmq
import json
import threading
from collections import deque
import socket

class MessageListener:
    def __init__(self, ip, port, buffer_size=100):
        self.ip = ip 
        self.port = port
        self.buffer = deque(maxlen=buffer_size)
        self.running = False
        self.thread = None

    def get_local_ip_address(self):
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Try to connect to a known address on the local network
            s.connect(("192.168.1.1", 80))  # You may need to change this address
            # Get the local IP address
            ip_address = s.getsockname()[0]
        except OSError:
            # Handle the case where the connection fails
            ip_address = "Unknown"
        finally:
            # Close the socket
            s.close()
        return ip_address

    # Start the listener my creating a new thread to process on
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._listen)
            self.thread.start()

    # safely close when program closes
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    # get data from buffer
    def getData(self):
        if self.buffer:
            return self.buffer.popleft()
        else:
            return None

    # THREAD - Connect socket and continuously listen and fill msg buffer
    def _listen(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)  # SUB socket subscribes to messages
        socket.connect(f"tcp://{self.ip}:{self.port}")
        socket.subscribe(b'')
        
        while self.running:
            try:
                message = socket.recv_string(flags=zmq.NOBLOCK)
                if message:
                    data = json.loads(message)
                    if len(self.buffer) == self.buffer.maxlen:
                        self.buffer.popleft()  # Remove the oldest message
                    self.buffer.append(data)
            except zmq.Again:
                pass

# if __name__ == "__main__":
#     listener = MessageListener("192.168.1.3", 5555)
#     listener.start()
    
#     try:
#         while True:
#             data = listener.getData()
#             if data:
#                 latitude = data["latitude"]
#                 longitude = data["longitude"]
#                 bearing = data["bearing"]
#                 print(f"(Latitude, Longitude): {latitude}, {longitude}\nBearing: {bearing}")
#     except KeyboardInterrupt:
#         listener.stop()
