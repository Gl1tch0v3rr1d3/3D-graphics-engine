# 3D Graphics Engine

A simple 3D wireframe rendering engine built with Pygame, featuring real-time rotation and projection of 3D objects onto a 2D screen.

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)


##  eatures

- Real-time 3D wireframe rendering
- Smooth Y-axis rotation animation
- Perspective projection with depth perception
- Multiple built-in 3D shapes (cube, pyramid, etc.)
- Configurable camera distance and rotation speed
- Clean, minimal Pygame implementation

## Installation

### Prerequisites
- Python 3.6+
- Pygame 2.0+

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/3D-graphics-engine.git
cd 3D-graphics-engine

# Install dependencies
pip install pygame
```

## Controls
- R: Reset rotation

- ↑/↓: Increase/decrease rotation speed

- ←/→: Change camera distance

- 1/2/3: Switch between different 3D models

- ESC: Exit

# Mathematical Pipeline
##  1. Vertex Representation (Model Space)
Each vertex is represented as:

```python
{'x': x, 'y': y, 'z': z}
```
All coordinates are centered around the origin (0, 0, 0) in normalized 3D space.

##  2. Rotation (XZ Plane / Y-Axis Rotation)
Rotation is applied in the XZ plane (around Y-axis):

```python
x' = x * cos(θ) - z * sin(θ)
z' = x * sin(θ) + z * cos(θ)
y' = y
```
##   Implementation:

```python
c = math.cos(angle)
s = math.sin(angle)
x_new = x * c - z * s
z_new = x * s + z * c
```

##   Translation Along Z-Axis (Camera Distance)
To ensure valid perspective projection:

```python
z' = z + d
```
Where d is the camera distance.


# #  Implementation:

``` python
translated_vertex = {'z': vertex['z'] + camera_distance}
```
##   4. Perspective Projection (3D → 2D)
Perspective division creates depth perception:

```python
x_proj = x / z
y_proj = y / z
```
##   Implementation:

```python
projected = {
    'x': vertex['x'] / vertex['z'],
    'y': vertex['y'] / vertex['z']
}
```
##   5. Screen Space Mapping
Normalized coordinates [-1, 1] → screen pixels:

```python
x_screen = (x + 1) / 2 * WIDTH
y_screen = (1 - (y + 1) / 2) * HEIGHT
```
##  Implementation:

```python
x_pixel = (projected['x'] + 1) / 2 * SCREEN_WIDTH
y_pixel = (1 - (projected['y'] + 1) / 2) * SCREEN_HEIGHT
```
##  6. Wireframe Rendering
Faces are defined as vertex indices. Edges connect consecutive vertices:

```python
for face in faces:
    for i in range(len(face)):
        start = vertices[face[i]]
        end = vertices[face[(i + 1) % len(face)]]
        pygame.draw.line(screen, COLOR, start, end)
```
# Project Structure

```
3d-graphics-engine/
├── 3d_engine.py          # Main engine implementation
├── shapes.py            # 3D shape definitions (cube, pyramid, etc.)
├── math_utils.py        # Math helper functions
├── README.md           # This file
└── requirements.txt    # Dependencies
```
# Supported 3D Models
- triangle (default)
- anything
- Custom shapes (easily extendable)

# Example Code
## Create a cube
```python
cube_vertices = [
    {'x': -1, 'y': -1, 'z': -1},
    {'x': 1, 'y': -1, 'z': -1},
    # ... more vertices
]

cube_faces = [
    [0, 1, 2, 3],  # Front face
    [4, 5, 6, 7],  # Back face
    # ... more faces
]

# Initialize engine
engine = Engine3D(vertices=cube_vertices, faces=cube_faces)
engine.run()
```
#Performance
- Rendering: 60 FPS target
- Max vertices: 1000+ on modern hardware
- Memory: Minimal footprint
- CPU usage: Single-threaded, optimized for clarity

# Contributing
- Contributions are welcome! Please feel free to submit a Pull Request.
