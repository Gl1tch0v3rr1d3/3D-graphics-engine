import pygame
import math
import sys

# Initialize Pygame
pygame.init()



# Constants
BACKGROUND = "#101010"
FOREGROUND = "#50FF50"
WIDTH, HEIGHT = 800, 800
FPS = 60

# screen display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Engine - SchadowRoot17")
clock = pygame.time.Clock()




# Convert hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

BACKGROUND = hex_to_rgb("#101010")
FOREGROUND = hex_to_rgb("#50FF50")
# x, y, z coordinates
# Each vertex is a dictionary with x, y, z keys
# list of points in 3D space
# starts from  0
vs = [
    {'x':  0.25, 'y':  0.25, 'z':  0.25}, #0
    {'x': -0.25, 'y':  0.25, 'z':  0.25}, #1
    {'x': -0.25, 'y': -0.25, 'z':  0.25}, #2
    {'x':  0.30, 'y':  0.30,  'z': 0.30}, #3
    {'x': -0.30, 'y': 0.30, 'z':  0.30},  #4
    {'x': -0.30, 'y': -0.30, 'z': 0.30}, #5
    ]
   

# Face indices
# Each face is a list of vertex indices
# Each face is defined by the indices of its vertices in the vs list
#start from  0
#drawing a triangle
fs = [
    [0, 1, 2],  # front face
    [3, 4, 5],  # back face
    [0, 1, 4, 3],  # top face
    [2, 5, 4, 1],  # left face
]

# Helper functions
def clear():
    screen.fill(BACKGROUND)

def point(pos, size=10):
    pygame.draw.rect(screen, FOREGROUND, 
                    (pos['x'] - size//2, pos['y'] - size//2, size, size))

def line(p1, p2):
    pygame.draw.line(screen, FOREGROUND, 
                    (int(p1['x']), int(p1['y'])), 
                    (int(p2['x']), int(p2['y'])), 3)

def screen_coords(p):
    """Convert -1..1 coordinates to screen coordinates"""
    return {
        'x': (p['x'] + 1) / 2 * WIDTH,
        'y': (1 - (p['y'] + 1) / 2) * HEIGHT,
    }

def project(p):
    """3D to 2D projection"""
    return {
        'x': p['x'] / p['z'],
        'y': p['y'] / p['z'],
    }

def translate_z(p, dz):
    return {'x': p['x'], 'y': p['y'], 'z': p['z'] + dz}

def rotate_xz(p, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return {
        'x': p['x'] * c - p['z'] * s,
        'y': p['y'],
        'z': p['x'] * s + p['z'] * c,
    }

# Game variables
dz = 1
angle = 0

def frame():
    global angle
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:  # ESC key
            if event.key == pygame.K_ESCAPE:
                print("\nExiting... \n")
                print("crated by ShadowRoot17 \n")
                print("inspired by Tsoding\n")
                pygame.quit()
                sys.exit()

    # Update
    dt = 1 / FPS
    angle += math.pi / 4 * dt  # Rotate slower
    #angle += 0 # to avoid unused movment 
    
    # Draw
    clear()
    
    # Draw edges
    for face in fs:
        for i in range(len(face)):
            a = vs[face[i]]
            b = vs[face[(i + 1) % len(face)]]
            
            # Transform vertices
            a_transformed = translate_z(rotate_xz(a, angle), dz)
            b_transformed = translate_z(rotate_xz(b, angle), dz)
            
            # Project to 2D and convert to screen coordinates
            a_screen = screen_coords(project(a_transformed))
            b_screen = screen_coords(project(b_transformed))
            
            line(a_screen, b_screen)
    
    # Draw vertices 
    # for v in vs:
    #     v_transformed = translate_z(rotate_xz(v, angle), dz)
    #     v_screen = screen_coords(project(v_transformed))
    #     point(v_screen)
    
    # Update display

    pygame.display.flip()



# Main game loop
def main():
    running = True
    while running:
        frame()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
