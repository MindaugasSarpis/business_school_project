import pygame
import numpy as np
import math

# Initialize Pygame
pygame.init()

# Set the screen size
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Rotating Cube")

# Define the cube vertices
vertices = np.array([
    [-1, -1, -1],
    [ 1, -1, -1],
    [ 1,  1, -1],
    [-1,  1, -1],
    [-1, -1,  1],
    [ 1, -1,  1],
    [ 1,  1,  1],
    [-1,  1,  1]
])

# Define the cube edges (pairs of vertices)
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

# Function to rotate the cube around the Y-axis
def rotate_y(theta):
    rotation_matrix = np.array([
        [math.cos(theta), 0, math.sin(theta)],
        [0, 1, 0],
        [-math.sin(theta), 0, math.cos(theta)]
    ])
    return vertices.dot(rotation_matrix.T)

# Function to project 3D points to 2D
def project_to_2d(vertices):
    projection = []
    for vertex in vertices:
        x, y, z = vertex
        factor = 400 / (z + 4)
        x_proj = x * factor + 400
        y_proj = -y * factor + 300
        projection.append((x_proj, y_proj))
    return projection

# Set up the main loop
running = True
theta = 0
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rotate the cube
    rotated_vertices = rotate_y(theta)
    
    # Project the 3D points to 2D
    projected_vertices = project_to_2d(rotated_vertices)

    # Fill the screen with a black background
    screen.fill((0, 0, 0))

    # Draw the cube edges
    for edge in edges:
        start, end = edge
        pygame.draw.line(screen, (255, 255, 255), projected_vertices[start], projected_vertices[end], 2)

    # Update the screen
    pygame.display.flip()

    # Increment the rotation angle
    theta += 0.02

    # Limit the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
