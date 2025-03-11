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
    # Line width for the corner arcs
    CORNER_LINE_WIDTH = 6
    
    # Draw straight borders first
    # Top line
    arcade.draw_line(
        CORNER_RADIUS, SCREEN_HEIGHT,
        SCREEN_WIDTH - CORNER_RADIUS, SCREEN_HEIGHT,
        arcade.color.WHITE, CORNER_LINE_WIDTH
    )
    
    # Bottom line
    arcade.draw_line(
        CORNER_RADIUS, 0,
        SCREEN_WIDTH - CORNER_RADIUS, 0,
        arcade.color.WHITE, CORNER_LINE_WIDTH
    )
    
    # Left line
    arcade.draw_line(
        0, CORNER_RADIUS,
        0, SCREEN_HEIGHT - CORNER_RADIUS,
        arcade.color.WHITE, CORNER_LINE_WIDTH
    )
    
    # Right line
    arcade.draw_line(
        SCREEN_WIDTH, CORNER_RADIUS,
        SCREEN_WIDTH, SCREEN_HEIGHT - CORNER_RADIUS,
        arcade.color.WHITE, CORNER_LINE_WIDTH
    )
    
    # Draw the corner arcs (slightly larger to overlap with lines)
    # Top-left corner
    arcade.draw_arc_outline(
        CORNER_RADIUS, SCREEN_HEIGHT - CORNER_RADIUS,
        CORNER_RADIUS * 2, CORNER_RADIUS * 2,
        arcade.color.WHITE, 90, 180, CORNER_LINE_WIDTH
    )
    
    # Top-right corner
    arcade.draw_arc_outline(
        SCREEN_WIDTH - CORNER_RADIUS, SCREEN_HEIGHT - CORNER_RADIUS,
        CORNER_RADIUS * 2, CORNER_RADIUS * 2,
        arcade.color.WHITE, 0, 90, CORNER_LINE_WIDTH
    )
    
    # Bottom-left corner
    arcade.draw_arc_outline(
        CORNER_RADIUS, CORNER_RADIUS,
        CORNER_RADIUS * 2, CORNER_RADIUS * 2,
        arcade.color.WHITE, 180, 270, CORNER_LINE_WIDTH
    )
    
    # Bottom-right corner
    arcade.draw_arc_outline(
        SCREEN_WIDTH - CORNER_RADIUS, CORNER_RADIUS,
        CORNER_RADIUS * 2, CORNER_RADIUS * 2,
        arcade.color.WHITE, 270, 360, CORNER_LINE_WIDTH
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

def get_rink_corner_positions():
    """Return the positions of the four corners of the rink"""
    return [
        (CORNER_RADIUS, CORNER_RADIUS),  # Bottom-left
        (SCREEN_WIDTH - CORNER_RADIUS, CORNER_RADIUS),  # Bottom-right
        (CORNER_RADIUS, SCREEN_HEIGHT - CORNER_RADIUS),  # Top-left
        (SCREEN_WIDTH - CORNER_RADIUS, SCREEN_HEIGHT - CORNER_RADIUS)  # Top-right
    ]

def is_point_in_corner_region(x, y):
    """Check if a point is in one of the corner regions of the rink"""
    # Check if in bottom-left corner region
    if x < CORNER_RADIUS and y < CORNER_RADIUS:
        return 0  # Bottom-left index
    # Check if in bottom-right corner region
    elif x > SCREEN_WIDTH - CORNER_RADIUS and y < CORNER_RADIUS:
        return 1  # Bottom-right index
    # Check if in top-left corner region
    elif x < CORNER_RADIUS and y > SCREEN_HEIGHT - CORNER_RADIUS:
        return 2  # Top-left index
    # Check if in top-right corner region
    elif x > SCREEN_WIDTH - CORNER_RADIUS and y > SCREEN_HEIGHT - CORNER_RADIUS:
        return 3  # Top-right index
    else:
        return -1  # Not in a corner region

def is_valid_position(x, y, radius):
    """Check if a position is valid within the rink boundaries, considering object radius"""
    # Get corner positions
    corner_positions = get_rink_corner_positions()
    
    # Check if point is in a corner region
    corner_index = is_point_in_corner_region(x, y)
    
    if corner_index >= 0:
        # If in a corner region, check distance to corner center
        corner_x, corner_y = corner_positions[corner_index]
        distance = math.sqrt((x - corner_x)**2 + (y - corner_y)**2)
        
        # Valid if distance + radius is less than or equal to corner radius
        # (this keeps the object fully inside the rounded corner)
        return distance + radius <= CORNER_RADIUS
    else:
        # If not in a corner region, check if within the straight edges
        return (radius <= x <= SCREEN_WIDTH - radius and 
                radius <= y <= SCREEN_HEIGHT - radius)

def constrain_to_rink(x, y, radius, half=None):
    """
    Constrain a position to stay within the rink boundaries.
    
    Parameters:
    - x, y: Current position
    - radius: Object radius
    - half: 'top' to constrain to top half, 'bottom' for bottom half, None for full rink
    
    Returns:
    - (x, y): Constrained position
    """
    # First constrain to half if specified
    if half == 'top':
        y = max(SCREEN_HEIGHT / 2 + radius, min(SCREEN_HEIGHT - radius, y))
    elif half == 'bottom':
        y = max(radius, min(SCREEN_HEIGHT / 2 - radius, y))
    
    # Basic boundary constraint for straight edges
    x = max(radius, min(SCREEN_WIDTH - radius, x))
    y = max(radius, min(SCREEN_HEIGHT - radius, y))
    
    # Check if in corner region
    corner_index = is_point_in_corner_region(x, y)
    if corner_index >= 0:
        corner_positions = get_rink_corner_positions()
        corner_x, corner_y = corner_positions[corner_index]
        
        # Calculate distance and direction from corner center to position
        dx = x - corner_x
        dy = y - corner_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # If outside valid area in corner, move back to valid position
        if distance > CORNER_RADIUS - radius:
            if distance > 0:  # Avoid division by zero
                # Normalize direction vector
                dx = dx / distance
                dy = dy / distance
                
                # Set position at valid distance from corner center
                x = corner_x + dx * (CORNER_RADIUS - radius)
                y = corner_y + dy * (CORNER_RADIUS - radius)
    
    return x, y