import pygame as py
import numpy as np
import pyaudio as pa
from sys import argv
import cv2

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
stp_x:int = 10
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

# Audio settings
CHUNK = 1024
FORMAT = pa.paInt16
CHANNELS = 2
RATE = 44100
THRESHOLD = 5000 if len(argv) < 2 else int(argv[1])

p = pa.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Initialize camera
cap = cv2.VideoCapture(0)
camera_width = 160
camera_height = 120

# Motion detection parameters
motion_threshold = 5000 if len(argv) < 3 else int(argv[2])
previous_frame = None

# Metronome settings
metronome_division:float = 0.25
metronome_speed:float = 96.0
shift_multiplier:float = 0.1 if len(argv) < 4 else int(argv[3])
shift_speed:int = int(metronome_division * metronome_speed * shift_multiplier)
metronome_activated:bool = False

# Game loop
clock = py.time.Clock()
running = True
while running:
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
        elif event.type == py.KEYDOWN:
            if event.key == py.K_t:
                metronome_activated = not(metronome_activated)

    keys = py.key.get_pressed()

    if   keys[py.K_UP]:    cur_zoom = min(max_zoom, cur_zoom * stp_zoom) if not(metronome_activated) else cur_zoom
    elif keys[py.K_DOWN]:  cur_zoom = max(min_zoom, cur_zoom / stp_zoom) if not(metronome_activated) else cur_zoom
    elif keys[py.K_LEFT]:  x = min(max_x, x + stp_x * cur_zoom) if not(metronome_activated) else x
    elif keys[py.K_RIGHT]: x = max(min_x, x - stp_x * cur_zoom) if not(metronome_activated) else x

    # Shift about metronome
    if metronome_activated:
        x = x = max(min_x, x - shift_speed * cur_zoom)

    # Check audio volume
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    volume = np.abs(data).mean()
    if volume > THRESHOLD: x = max(min_x, x - stp_x * cur_zoom) if not(metronome_activated) else x

    # Fill the background with white
    screen.fill(background_color)

    # Draw the image onto the screen
    screen.blit(resize_image(image, cur_zoom), (x, y))

    # Read camera frame
    ret, frame = cap.read()
    if ret:
        # Convert frame to RGB format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert OpenCV numpy array to Pygame surface
        surf = py.surfarray.make_surface(frame)
        
        # Rotate the surface using Pygame's transform functions
        rotated_surf = py.transform.rotate(surf, 270)
        
        # Resize the rotated surface to fit in the corner
        resized_surf = py.transform.scale(rotated_surf, (camera_width, camera_height))
        
        # Blit the rotated and resized surface to the main screen
        screen.blit(resized_surf, (window_width - camera_width, window_height - camera_height))

        # Perform motion detection
        if previous_frame is not None:
            diff = cv2.absdiff(previous_frame, frame)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, motion_threshold, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Move the main image right if motion is detected
            if contours: x = max(min_x, x - stp_x * cur_zoom)

        previous_frame = frame

    # Update the display
    py.display.flip()
    clock.tick(60)

# Quit py
py.quit()
cap.release()
