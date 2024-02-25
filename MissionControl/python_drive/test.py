import pygame
from pygame.locals import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from threading import Thread, Event
import queue
import socket

# Pygame setup
pygame.init()
pygame.display.set_caption("Pygame Window")
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Data queue for communication between threads
data_queue = queue.Queue()

# Function to receive data and update the queue
def receive_data():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        data, _ = sock.recvfrom(1024)
        data_queue.put(data.decode("utf-8"))

# Thread for receiving data
receive_thread = Thread(target=receive_data)
receive_thread.daemon = True
receive_thread.start()

# Function to update Matplotlib plot
def update_plot():
    fig, ax = plt.subplots()
    canvas = FigureCanvas(fig)
    while True:
        try:
            data_points = []
            while not data_queue.empty():
                data_points.append(float(data_queue.get()))
            if data_points:
                ax.clear()
                ax.plot(data_points)
                canvas.draw()
                renderer = canvas.get_renderer()
                raw_data = renderer.tostring_rgb()
                size = canvas.get_width_height()
                pygame_surface = pygame.image.fromstring(raw_data, size, "RGB")
                screen.blit(pygame_surface, (0, 0))
                pygame.display.flip()
        except Exception as e:
            print("Error in update_plot:", e)

# Thread for updating plot
plot_thread = Thread(target=update_plot)
plot_thread.daemon = True
plot_thread.start()

# Main Pygame loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update Pygame display
    screen.fill((255, 255, 255))
    pygame.display.flip()
    clock.tick(30)

# Clean up
pygame.quit()
