import os
import math
import wave
import struct
import random
import arcade
from constants import SOUND_FILES, CORNER_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT

def create_default_sound_files():
    """Create placeholder sound files if they don't exist"""
    # Create sounds directory if it doesn't exist
    os.makedirs("sounds", exist_ok=True)
    
    # Check if each file exists, if not create a placeholder
    for sound_file in SOUND_FILES:
        if not os.path.exists(sound_file):
            # Create an empty placeholder WAV file
            try:
                # Create a simple beep sound
                sample_rate = 44100
                duration = 0.2  # seconds
                frequency = 440.0  # A4 note
                
                # Open WAV file for writing
                with wave.open(sound_file, 'w') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 2 bytes per sample
                    wav_file.setframerate(sample_rate)
                    
                    # Generate sine wave
                    for i in range(int(duration * sample_rate)):
                        value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
                        data = struct.pack('<h', value)
                        wav_file.writeframes(data)
            except Exception as e:
                print(f"Could not create sound file {sound_file}: {e}")
                print("You may need to provide your own sound files in the 'sounds' directory.")

def spawn_particles(x, y, color, count=10):
    """Creates a list of particle dictionaries"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        lifetime = random.uniform(0.2, 0.5)
        radius = random.uniform(2, 5)
        
        particles.append({
            'x': x,
            'y': y,
            'dx': math.cos(angle) * speed,
            'dy': math.sin(angle) * speed,
            'radius': radius,
            'original_radius': radius,
            'lifetime': lifetime,
            'max_lifetime': lifetime,
            'color': color
        })
    return particles

def update_particles(particles, delta_time):
    """Updates all particles and returns the updated list"""
    for i in range(len(particles) - 1, -1, -1):
        particle = particles[i]
        
        # Move particle
        particle['x'] += particle['dx']
        particle['y'] += particle['dy']
        
        # Reduce lifetime
        particle['lifetime'] -= delta_time
        
        # Remove particle if lifetime is up
        if particle['lifetime'] <= 0:
            particles.pop(i)
        else:
            # Shrink particle as it ages
            particle['radius'] = particle['original_radius'] * (particle['lifetime'] / particle['max_lifetime'])
    
    return particles

def draw_rounded_hockey_rink():
    """Draw a hockey rink with rounded corners"""
    # Draw the main outline with rounded corners
    # Top-left corner
    arcade.draw_arc_outline(
        CORNER_RADIUS, SCREEN_HEIGHT - CORNER_RADIUS,
        CORNER_RADIUS * 2, CORNER_RADIUS * 2,
        arcade.color.WHITE, 90, 180, 4
    )
    
    # Top-right corner
    arcade.draw_arc_outline(
        SCREEN_WIDTH - CORNER_RADIUS, SCREEN_HEIGHT - CORNER_RADIUS,
        CORNER_RADIUS * 2, CORNER_RADIUS * 2,
        arcade.color.WHITE, 180, 270, 4
    )
    
    # Bottom-left corner
    arcade.draw_arc_outline(
        CORNER_RADIUS, CORNER_RADIUS,
        CORNER_RADIUS * 2, CORNER_RADIUS * 2,
        arcade.color.WHITE, 0, 90, 4
    )
    
    # Bottom-right corner
    arcade.draw_arc_outline(
        SCREEN_WIDTH - CORNER_RADIUS, CORNER_RADIUS,
        CORNER_RADIUS * 2, CORNER_RADIUS * 2,
        arcade.color.WHITE, 360, 0, 4
    )
    
    # Connect the arcs with straight lines
    # Top line
    arcade.draw_line(
        CORNER_RADIUS, SCREEN_HEIGHT,
        SCREEN_WIDTH - CORNER_RADIUS, SCREEN_HEIGHT,
        arcade.color.WHITE, 4
    )
    
    # Bottom line
    arcade.draw_line(
        CORNER_RADIUS, 0,
        SCREEN_WIDTH - CORNER_RADIUS, 0,
        arcade.color.WHITE, 4
    )
    
    # Left line
    arcade.draw_line(
        0, CORNER_RADIUS,
        0, SCREEN_HEIGHT - CORNER_RADIUS,
        arcade.color.WHITE, 4
    )
    
    # Right line
    arcade.draw_line(
        SCREEN_WIDTH, CORNER_RADIUS,
        SCREEN_WIDTH, SCREEN_HEIGHT - CORNER_RADIUS,
        arcade.color.WHITE, 4
    )
    
    # Draw center line
    arcade.draw_line(
        0, SCREEN_HEIGHT // 2,
        SCREEN_WIDTH, SCREEN_HEIGHT // 2,
        arcade.color.WHITE, 2
    )
    
    # Draw center circle
    arcade.draw_circle_outline(
        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
        100, arcade.color.WHITE, 2
    )

def is_point_inside_rounded_rink(x, y):
    """Check if a point is inside the rounded hockey rink"""
    # Check if the point is in one of the corners
    if x < CORNER_RADIUS and y < CORNER_RADIUS:
        # Bottom-left corner
        distance = math.sqrt((x - CORNER_RADIUS)**2 + (y - CORNER_RADIUS)**2)
        return distance <= CORNER_RADIUS
    elif x > SCREEN_WIDTH - CORNER_RADIUS and y < CORNER_RADIUS:
        # Bottom-right corner
        distance = math.sqrt((x - (SCREEN_WIDTH - CORNER_RADIUS))**2 + (y - CORNER_RADIUS)**2)
        return distance <= CORNER_RADIUS
    elif x < CORNER_RADIUS and y > SCREEN_HEIGHT - CORNER_RADIUS:
        # Top-left corner
        distance = math.sqrt((x - CORNER_RADIUS)**2 + (y - (SCREEN_HEIGHT - CORNER_RADIUS))**2)
        return distance <= CORNER_RADIUS
    elif x > SCREEN_WIDTH - CORNER_RADIUS and y > SCREEN_HEIGHT - CORNER_RADIUS:
        # Top-right corner
        distance = math.sqrt((x - (SCREEN_WIDTH - CORNER_RADIUS))**2 + (y - (SCREEN_HEIGHT - CORNER_RADIUS))**2)
        return distance <= CORNER_RADIUS
    else:
        # If not in a corner, check if within the rectangle bounds
        return (CORNER_RADIUS <= x <= SCREEN_WIDTH - CORNER_RADIUS or 
                CORNER_RADIUS <= y <= SCREEN_HEIGHT - CORNER_RADIUS)