#THis code has to be used on pi
#This is a fully working calibrated code (both for pan and tilt)
#there is a small offeset in pan which is becasue of motor precsion issue

import socket
import pigpio  # For controlling servos
import time
import math

# Raspberry Pi connection details
raspberry_pi_ip = '172.20.10.2'  # Your Pi's IP address
port = 5005  # Port number for receiving data

# Setup GPIO pins for servo motors
PAN_PIN = 13  # GPIO13 for pan
TILT_PIN = 12  # GPIO12 for tilt

# Initialize pigpio
pi = pigpio.pi()

if not pi.connected:
    exit(0)

# Servo motor angle limits
PAN_CENTER = 112
TILT_CENTER = 105
PAN_MIN = 55
PAN_MAX = 160
TILT_MIN = 70
TILT_MAX = 140

# Camera field of view (FOV)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
H_FOV = 95  # Horizontal field of view in degrees
V_FOV = 70  # Vertical field of view in degrees

# Linear offset parameters
OFFSET_AT_7M = 0.65  # Offset of 0.5 meters at 7 meters distance
MIN_DISTANCE = 1.0  # Distance where offset is 0 meters
MAX_DISTANCE = 6.0  # Maximum distance for the offset calculation

# Function to calculate tilt angle offset based on distance
def calculate_tilt_offset(distance):
    if distance < MIN_DISTANCE:
        return 0  # No correction for distances less than 1 meter
    elif distance > MAX_DISTANCE:
        distance = MAX_DISTANCE  # Cap at 7 meters
    
    # Linear offset (height) calculation
    height_offset = (OFFSET_AT_7M * (distance - MIN_DISTANCE)) / (MAX_DISTANCE - MIN_DISTANCE)
    
    # Calculate angle offset (degrees) using trigonometry
    tilt_offset = math.degrees(math.atan(height_offset / distance))
    
    return tilt_offset

# Function to convert coordinates to angles
def coords_to_angles(x, y, distance):
    # Pan (horizontal) mapping
    pan_angle = ((x / CAMERA_WIDTH) * (PAN_MAX - PAN_MIN)) + PAN_MIN

    # Tilt (vertical) mapping
    tilt_angle = ((y / CAMERA_HEIGHT) * (TILT_MAX - TILT_MIN)) + TILT_MIN
    
    # Apply tilt offset correction in reverse direction based on the distance
    tilt_angle -= calculate_tilt_offset(distance)  # Subtracting the offset to move in the opposite direction

    # Constrain angles to motor limits
    pan_angle = max(min(pan_angle, PAN_MAX), PAN_MIN)
    tilt_angle = max(min(tilt_angle, TILT_MAX), TILT_MIN)

    return pan_angle, tilt_angle

# Function to set servo angles
def set_servo_angle(pin, angle):
    # Convert angle to PWM pulse width (1000-2000us)
    pulse_width = 1000 + (angle / 180.0) * 1000
    pi.set_servo_pulsewidth(pin, pulse_width)

# UDP socket setup for receiving coordinates
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((raspberry_pi_ip, port))

print(f"Listening for data on {raspberry_pi_ip}:{port}...")

try:
    while True:
        # Receive data from the camera code (coordinates in format "x,y,distance")
        data, addr = sock.recvfrom(1024)
        coord_data = data.decode().strip().split(',')
        
        if len(coord_data) == 3:
            x, y, distance = map(float, coord_data)
            
            # Calculate pan and tilt angles
            pan_angle, tilt_angle = coords_to_angles(x, y, distance)
            
            # Set servo angles
            set_servo_angle(PAN_PIN, pan_angle)
            set_servo_angle(TILT_PIN, tilt_angle)
            
            # Print the current pan, tilt angles, and depth (distance) value
            print(f"Pan: {pan_angle:.2f}Â°, Tilt: {tilt_angle:.2f}Â°, Depth: {distance:.2f} meters")

        time.sleep(0.1)

finally:
    # Clean up
    pi.set_servo_pulsewidth(PAN_PIN, 0)
    pi.set_servo_pulsewidth(TILT_PIN, 0)
    sock.close()
    pi.stop()
