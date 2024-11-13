import pygame as py
import numpy as np
import pyaudio as pa
from sys import argv
import time

# Initialize py
py.init()

# Load the image and its background color
image_path = "Outer_Wilds.png"
try: image = py.image.load(image_path)
except py.error as e: raise Exception(f"Error loading image: {e}")
background_color = image.get_at((0,0))[:3]

# Get the dimensions of the image
image_width, image_height = image.get_size()

# Set up the display window as 16:9
window_width = (image_height * 32) // 9
window_height = image_height * 2
screen = py.display.set_mode((window_width, window_height))

# Coordinates of the picture
x:int = 0 # Serves as shift among music sheet
y:int = image_height // 2 # Middle of the screen among Y axis
stp_x:int = 1
max_x:int = 0
min_x:int = window_width - image_width

# Zoom options
min_zoom:float = 0.2
max_zoom:float = 4.0
stp_zoom:float = 1.1
cur_zoom:float = 1.0

# Resize the image
def resize_image(image:py.Surface, scale:float) -> py.Surface:
    width:int = int(image.get_width() * scale)
    height:int= int(image.get_height()* scale)
    return py.transform.scale(image, (width, height))


# Audio settings for linux
# CHUNK = 1024
# FORMAT = pa.paInt16
# CHANNELS = 2
# RATE = 44100
# THRESHOLD = 5000 if len(argv) < 2 else int(argv[1])


# Audio settings for MAC
CHUNK = 4096
FORMAT = pa.paInt16
CHANNELS = 1
RATE = 22050
THRESHOLD = 400 if len(argv) < 2 else int(argv[1])

p = pa.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Game loop
clock = py.time.Clock()
running = True
while running:
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
    
    keys = py.key.get_pressed()

    if   keys[py.K_UP]:    cur_zoom = min(max_zoom, cur_zoom * stp_zoom)
    elif keys[py.K_DOWN]:  cur_zoom = max(min_zoom, cur_zoom / stp_zoom)
    elif keys[py.K_LEFT]:  x = min(max_x, x + stp_x)
    elif keys[py.K_RIGHT]: x = max(min_x, x - stp_x)

    # Check audio volume
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    volume = np.abs(data).mean()
    if volume > THRESHOLD: x = max(min_x, x - stp_x)

    # Fill the background with white
    screen.fill(background_color)

    # Draw the image onto the screen
    screen.blit(resize_image(image, cur_zoom), (x, y))

    # Update the display
    py.display.flip()
    clock.tick(60)

# Quit py
py.quit()
