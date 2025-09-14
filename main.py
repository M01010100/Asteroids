import sys
import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
import time

def draw_button(screen, text, rect, color="white", hover_color="gray"):
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, rect)
    else:
        pygame.draw.rect(screen, color, rect)
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, "black")
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    game_state = PLAYING

    # Initialize game objects and time tracking
    def init_game():
        updatable = pygame.sprite.Group()
        drawable = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        shots = pygame.sprite.Group()

        Asteroid.containers = (asteroids, updatable, drawable)
        Shot.containers = (shots, updatable, drawable)
        AsteroidField.containers = updatable
        asteroid_field = AsteroidField()

        Player.containers = updatable, drawable
        
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)    
        
        # Start tracking time
        start_time = time.time()
        
        return {
            'updatable': updatable,
            'drawable': drawable,
            'asteroids': asteroids,
            'shots': shots,
            'asteroid_field': asteroid_field,
            'player': player,
            'start_time': start_time
        }
    
    # Initialize game objects
    game_objects = init_game()
    
    dt = 0
    game_time = 0  # Store final game time

    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            # Key handling when in game over state
            if game_state == GAME_OVER and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Restart the game
                    game_objects = init_game()
                    game_state = PLAYING
                elif event.key == pygame.K_q:
                    # Quit the game
                    pygame.quit()
                    sys.exit()
        
        if game_state == PLAYING:
            # Game playing logic
            game_objects['updatable'].update(dt)

            for asteroid in game_objects['asteroids']:
                if asteroid.collide(game_objects['player']):
                    print("Game over!")
                    game_state = GAME_OVER
                    game_time = time.time() - game_objects['start_time']
            
            for asteroid in game_objects['asteroids']:
                for shot in game_objects['shots']:
                    if asteroid.collide(shot):
                        shot.kill()
                        asteroid.split()
                        break  
                    
            screen.fill("black")
            
            for obj in game_objects['drawable']:
                obj.draw(screen)

        elif game_state == GAME_OVER:
            screen.fill("black")
            
            # Draw "GAME OVER" text
            font_large = pygame.font.Font(None, 72)
            game_over_text = font_large.render("GAME OVER", True, "red")
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 80))
            screen.blit(game_over_text, text_rect)
            
            font_medium = pygame.font.Font(None, 48)
            minutes = int(game_time) // 60
            seconds = int(game_time) % 60
            time_text = font_medium.render(f"Time Played: {minutes}:{seconds:02d}", True, "white")
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(time_text, time_rect)
            
            if int(time.time() * 2) % 2 == 0:
                font_small = pygame.font.Font(None, 36)
                restart_text = font_small.render("Press SPACE to continue", True, "white")
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60))
                screen.blit(restart_text, restart_rect)
                
                # Show quit instruction
                quit_text = font_small.render("Press Q to quit", True, "white")
                quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100))
                screen.blit(quit_text, quit_rect)

        pygame.display.flip()

        # limit the framerate to 60 FPS
        dt = clock.tick(60) / 1000

if __name__ == "__main__":
    main()
