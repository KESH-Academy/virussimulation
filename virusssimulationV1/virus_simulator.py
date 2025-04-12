import pygame
import random
import math
import sys
from datetime import datetime

# Constants
WINDOW_WIDTH = 1920  # Fullscreen width
WINDOW_HEIGHT = 1080  # Fullscreen height
FPS = 60
UI_PANEL_WIDTH = 300

# Colors
BLUE = (0, 0, 255)    # Recovered
GREEN = (0, 255, 0)   # Healthy
RED = (255, 0, 0)     # Infected
BLACK = (0, 0, 0)     # Dead
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)  # Buildings
LIGHT_GRAY = (220, 220, 220)  # Streets
BROWN = (139, 69, 19)  # Cemetery
SLIDER_COLOR = (100, 100, 255)
SLIDER_HANDLE_COLOR = (50, 50, 200)

class Building:
    def __init__(self, x, y, width, height, type_):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type_  # 'hospital', 'cemetery', 'building'
        self.color = DARK_GRAY if type_ == 'building' else RED if type_ == 'hospital' else BROWN
        self.label = 'H' if type_ == 'hospital' else 'C' if type_ == 'cemetery' else ''

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.label:
            text = font.render(self.label, True, WHITE)
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)

class Person:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.status = "healthy"  # healthy, infected, dead, recovered
        self.infection_time = 0
        self.size = 5
        self.recovery_time = 10
        self.death_chance = 0.2
        self.recovery_chance = 0.8  # Default recovery chance
        self.infection_radius = 10
        self.target = None
        self.target_type = None

    def move(self, buildings):
        if self.status != "dead":
            if self.target:
                # Move towards target
                dx = self.target[0] - self.x
                dy = self.target[1] - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 5:
                    self.vx = dx/dist * 2
                    self.vy = dy/dist * 2
                else:
                    self.target = None
                    self.target_type = None
            else:
                # Random wandering
                self.vx += random.uniform(-0.2, 0.2)
                self.vy += random.uniform(-0.2, 0.2)
                # Limit speed
                speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
                if speed > 2:
                    self.vx = self.vx/speed * 2
                    self.vy = self.vy/speed * 2

            self.x += self.vx
            self.y += self.vy

            # Keep within screen bounds
            self.x = max(0, min(WINDOW_WIDTH, self.x))
            self.y = max(0, min(WINDOW_HEIGHT, self.y))

            # Avoid buildings
            for building in buildings:
                if building.rect.collidepoint(self.x, self.y):
                    if self.x < building.rect.left:
                        self.x = building.rect.left - 1
                    elif self.x > building.rect.right:
                        self.x = building.rect.right + 1
                    if self.y < building.rect.top:
                        self.y = building.rect.top - 1
                    elif self.y > building.rect.bottom:
                        self.y = building.rect.bottom + 1

    def update(self, dt, people, buildings):
        if self.status == "infected":
            self.infection_time += dt
            
            # Infected people try to go to hospital
            if not self.target and random.random() < 0.01:
                for building in buildings:
                    if building.type == 'hospital':
                        self.target = (building.rect.centerx, building.rect.centery)
                        self.target_type = 'hospital'
                        break
            
            if self.infection_time >= self.recovery_time:
                if random.random() < self.death_chance:
                    self.status = "dead"
                else:
                    if random.random() < self.recovery_chance:
                        self.status = "recovered"
                    else:
                        self.status = "healthy"
                    self.infection_time = 0
            
            # Try to infect others
            for person in people:
                if person.status == "healthy":
                    distance = math.sqrt((self.x - person.x)**2 + (self.y - person.y)**2)
                    if distance < self.infection_radius and random.random() < 0.4:
                        person.status = "infected"

    def draw(self, screen):
        color = GREEN if self.status == "healthy" else RED if self.status == "infected" else BLACK if self.status == "dead" else BLUE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.handle_rect = pygame.Rect(x + (width - 10) * (initial_val - min_val) / (max_val - min_val), 
                                     y, 10, 20)

    def draw(self, screen, font):
        # Draw slider track
        pygame.draw.rect(screen, GRAY, self.rect)
        # Draw slider handle
        pygame.draw.rect(screen, SLIDER_HANDLE_COLOR, self.handle_rect)
        # Draw label and value
        label_text = font.render(f"{self.label}: {self.value:.1f}", True, BLACK)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update handle position and value
            x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width - 10))
            self.handle_rect.x = x
            # Calculate value based on handle position
            self.value = self.min_val + (self.max_val - self.min_val) * (x - self.rect.x) / (self.rect.width - 10)
            return True
        return False

class Button:
    def __init__(self, x, y, width, height, text, color=GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.is_hovered = False

    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border
        text = font.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Virus Spread Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = True  # Start paused
        self.simulation_running = False
        
        # Buildings
        self.buildings = []
        self.create_city_layout()
        
        # People
        self.people = []
        
        # Parameters
        self.parameters = {
            "population_size": 100,
            "infection_radius": 10,
            "infection_chance": 0.4,
            "death_chance": 0.2,
            "recovery_time": 10,
            "movement_speed": 2
        }
        
        # Statistics
        self.stats = {
            "healthy": [],
            "infected": [],
            "dead": []
        }
        self.time = 0
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.run_button = pygame.Rect(WINDOW_WIDTH - 150, 10, 140, 40)
        self.parameter_buttons = {}
        self.create_parameter_buttons()
        
        # Create UI elements
        self.create_ui_elements()

    def create_city_layout(self):
        # Create streets
        street_width = 100
        for x in range(0, WINDOW_WIDTH, 300):
            pygame.draw.rect(self.screen, LIGHT_GRAY, (x, 0, street_width, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, 300):
            pygame.draw.rect(self.screen, LIGHT_GRAY, (0, y, WINDOW_WIDTH, street_width))
        
        # Create buildings
        for x in range(100, WINDOW_WIDTH - 100, 300):
            for y in range(100, WINDOW_HEIGHT - 100, 300):
                if random.random() < 0.8:  # 80% chance of building
                    self.buildings.append(Building(x, y, 100, 100, 'building'))
        
        # Create hospital
        self.buildings.append(Building(WINDOW_WIDTH - 200, 100, 150, 150, 'hospital'))
        
        # Create cemetery
        self.buildings.append(Building(100, WINDOW_HEIGHT - 200, 150, 150, 'cemetery'))

    def create_parameter_buttons(self):
        y = 60
        for param, value in self.parameters.items():
            self.parameter_buttons[param] = {
                "rect": pygame.Rect(10, y, 200, 30),
                "value": value,
                "min": 0,
                "max": 100 if param in ["infection_chance", "death_chance"] else 1000
            }
            y += 40

    def create_ui_elements(self):
        # Sliders
        self.sliders = [
            Slider(20, 100, 260, 10, 500, 100, "Population Size"),
            Slider(20, 160, 260, 0, 100, 10, "Initial Infected %"),
            Slider(20, 220, 260, 1, 20, 10, "Infection Radius"),
            Slider(20, 280, 260, 0, 100, 40, "Infection Chance %"),
            Slider(20, 340, 260, 0, 100, 20, "Death Chance %"),
            Slider(20, 400, 260, 0, 100, 80, "Recovery Chance %"),
            Slider(20, 460, 260, 1, 30, 10, "Recovery Time"),
            Slider(20, 520, 260, 1, 5, 2, "Movement Speed")
        ]
        
        # Buttons
        self.buttons = [
            Button(20, 580, 260, 50, "Start Simulation"),
            Button(20, 640, 260, 50, "Reset", color=(255, 100, 100))
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
            
            # Handle UI elements
            for slider in self.sliders:
                slider.handle_event(event)
            
            for button in self.buttons:
                if button.handle_event(event):
                    if button.text == "Start Simulation" and not self.simulation_running:
                        self.start_simulation()
                    elif button.text == "Reset":
                        self.reset_simulation()

    def start_simulation(self):
        self.simulation_running = True
        self.paused = False
        
        # Create initial population based on slider value
        num_people = int(self.sliders[0].value)  # Population size from slider
        num_infected = int(num_people * self.sliders[1].value / 100)  # Initial infected from slider
        
        for _ in range(num_people):
            x = random.randint(UI_PANEL_WIDTH, WINDOW_WIDTH - 100)
            y = random.randint(0, WINDOW_HEIGHT - 100)
            person = Person(x, y)
            
            # Set initial infection status
            if num_infected > 0:
                person.status = "infected"
                num_infected -= 1
            
            # Apply slider values
            person.infection_radius = self.sliders[2].value
            person.death_chance = self.sliders[4].value / 100
            person.recovery_chance = self.sliders[5].value / 100
            person.recovery_time = self.sliders[6].value
            person.vx = random.uniform(-self.sliders[7].value, self.sliders[7].value)
            person.vy = random.uniform(-self.sliders[7].value, self.sliders[7].value)
            
            self.people.append(person)

    def draw_ui(self):
        # Draw UI panel background
        pygame.draw.rect(self.screen, WHITE, (0, 0, UI_PANEL_WIDTH, WINDOW_HEIGHT))
        pygame.draw.rect(self.screen, BLACK, (0, 0, UI_PANEL_WIDTH, WINDOW_HEIGHT), 2)
        
        # Draw title
        title = self.font.render("Virus Simulator", True, BLACK)
        self.screen.blit(title, (UI_PANEL_WIDTH//2 - title.get_width()//2, 20))
        
        # Draw sliders
        for slider in self.sliders:
            slider.draw(self.screen, self.small_font)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, self.font)
        
        # Draw stats below the reset button
        stats_y = 700  # Position below the reset button
        stats = [
            f"Healthy: {sum(1 for p in self.people if p.status == 'healthy')}",
            f"Infected: {sum(1 for p in self.people if p.status == 'infected')}",
            f"Recovered: {sum(1 for p in self.people if p.status == 'recovered')}",
            f"Dead: {sum(1 for p in self.people if p.status == 'dead')}",
            f"Total: {len(self.people)}"
        ]
        
        # Draw colored squares next to stats
        colors = [GREEN, RED, BLUE, BLACK, BLACK]
        for i, (stat, color) in enumerate(zip(stats, colors)):
            # Draw colored square
            pygame.draw.rect(self.screen, color, (20, stats_y + i * 30, 15, 15))
            # Draw stat text
            text = self.small_font.render(stat, True, BLACK)
            self.screen.blit(text, (40, stats_y + i * 30))

    def reset_simulation(self):
        self.people = []
        self.stats = {"healthy": [], "infected": [], "dead": []}
        self.time = 0
        self.simulation_running = False
        self.paused = True

    def update_stats(self):
        healthy = sum(1 for p in self.people if p.status == "healthy")
        infected = sum(1 for p in self.people if p.status == "infected")
        dead = sum(1 for p in self.people if p.status == "dead")
        
        self.stats["healthy"].append(healthy)
        self.stats["infected"].append(infected)
        self.stats["dead"].append(dead)

    def run(self):
        while self.running:
            dt = 1/FPS
            self.handle_events()
            
            # Draw everything
            self.screen.fill(WHITE)
            
            # Draw buildings
            for building in self.buildings:
                building.draw(self.screen, self.font)
            
            if not self.paused and self.simulation_running:
                self.time += dt
                
                # Update all people
                for person in self.people:
                    person.move(self.buildings)
                    person.update(dt, self.people, self.buildings)
                
                self.update_stats()
            
            # Draw people
            for person in self.people:
                person.draw(self.screen)
            
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    simulation = Simulation()
    simulation.run() 