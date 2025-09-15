import sys
import pygame
import random
import csv
import os
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
import time

# ASCII Art for "ASTEROIDS"
ASTEROIDS_ASCII = [
    "    _    ____ _____ _____ ____   ___ ___ ____  ____  ",
    "   / \\  / ___|_   _| ____|  _ \\ / _ \\_ _|  _ \\/ ___| ",
    "  / _ \\ \\___ \\ | | |  _| | |_) | | | | || | | \\___ \\ ",
    " / ___ \\ ___) || | | |___|  _ <| |_| | || |_| |___) |",
    "/_/   \\_\\____/ |_| |_____|_| \\_\\\\___/___|____/|____/ "
]

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

def load_high_scores():
    """Load high scores from CSV file"""
    scores = []
    try:
        if os.path.exists('high_scores.csv'):
            with open('high_scores.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 2:
                        name, score = row
                        scores.append((name, float(score)))
    except Exception as e:
        print(f"Error loading high scores: {e}")
    
    # Sort by score (descending)
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:5]  # Return top 5 scores

def save_high_score(name, score):
    scores = load_high_scores()
    scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:5]  # Keep only top 5
    
    try:
        with open('high_scores.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for name, score in scores:
                writer.writerow([name, score])
    except Exception as e:
        print(f"Error saving high scores: {e}")

def is_high_score(score, high_scores):
    if len(high_scores) < 5:
        return True
    return score > high_scores[-1][1]

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    high_scores = load_high_scores()

    game_state = WELCOME

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
    
    game_objects = None
    dt = 0
    game_time = 0  # Store final game time
    player_name = ""  # For high score entry
    
    welcome_asteroids = []
    for _ in range(5):
        pos = pygame.Vector2(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT)
        )
        vel = pygame.Vector2(
            random.uniform(-25, 25),
            random.uniform(-25, 25)
        )
        radius = random.uniform(10, 30)
        welcome_asteroids.append({'pos': pos, 'vel': vel, 'radius': radius})

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if game_state == ENTER_NAME:
                    if event.key == pygame.K_RETURN and player_name:
                        save_high_score(player_name, game_time)
                        high_scores = load_high_scores()
                        game_state = WELCOME
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.unicode.isalnum() or event.unicode == ' ':
                        if len(player_name) < 15:
                            player_name += event.unicode
                else:
                    if event.key == pygame.K_SPACE:
                        if game_state == WELCOME:
                            game_objects = init_game()
                            game_state = PLAYING
                        elif game_state == GAME_OVER:
                            if is_high_score(game_time, high_scores):
                                player_name = ""
                                game_state = ENTER_NAME
                            else:
                                game_objects = init_game()
                                game_state = PLAYING
                    elif event.key == pygame.K_q and game_state in [WELCOME, GAME_OVER]:
                        pygame.quit()
                        sys.exit()
        
        screen.fill("black")
        
        if game_state == WELCOME:
            for asteroid in welcome_asteroids:
                asteroid['pos'] += asteroid['vel'] * dt
                
                if asteroid['pos'].x < 0:
                    asteroid['pos'].x = SCREEN_WIDTH
                elif asteroid['pos'].x > SCREEN_WIDTH:
                    asteroid['pos'].x = 0
                if asteroid['pos'].y < 0:
                    asteroid['pos'].y = SCREEN_HEIGHT
                elif asteroid['pos'].y > SCREEN_HEIGHT:
                    asteroid['pos'].y = 0
                
                pygame.draw.circle(screen, "white", (int(asteroid['pos'].x), int(asteroid['pos'].y)), 
                                  int(asteroid['radius']), 1)
            
            font_ascii = pygame.font.Font(None, 24)  # Monospace font
            for i, line in enumerate(ASTEROIDS_ASCII):
                text_surface = font_ascii.render(line, True, "white")
                screen.blit(text_surface, (SCREEN_WIDTH//2 - text_surface.get_width()//2, SCREEN_HEIGHT//4 + i*24))
            
            font_score = pygame.font.Font(None, 36)
            title_text = font_score.render("HIGH SCORES", True, "yellow")
            screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            
            for i, (name, score) in enumerate(high_scores):
                minutes = int(score) // 60
                seconds = int(score) % 60
                score_text = font_score.render(f"{i+1}. {name}: {minutes}:{seconds:02d}", True, "white")
                screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 20 + i*30))
            
            font_instr = pygame.font.Font(None, 36)
            if int(time.time() * 2) % 2 == 0:  # Make it blink
                play_text = font_instr.render("Press SPACE to play", True, "white")
                play_rect = play_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT * 4//5))
                screen.blit(play_text, play_rect)
                
                quit_text = font_instr.render("Press Q to quit", True, "white")
                quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT * 4//5 + 40))
                screen.blit(quit_text, quit_rect)
                
        elif game_state == PLAYING:
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
            
            for obj in game_objects['drawable']:
                obj.draw(screen)

        elif game_state == GAME_OVER:
            font_large = pygame.font.Font(None, 72)
            game_over_text = font_large.render("GAME OVER", True, "red")
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/5))
            screen.blit(game_over_text, text_rect)
            
            font_medium = pygame.font.Font(None, 48)
            minutes = int(game_time) // 60
            seconds = int(game_time) % 60
            time_text = font_medium.render(f"Time Played: {minutes}:{seconds:02d}", True, "white")
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/5 + 60))
            screen.blit(time_text, time_rect)
            
            score_rank = "Not in top 5"
            for i, (_, score) in enumerate(high_scores):
                if game_time > score:
                    score_rank = f"#{i+1}"
                    break
            
            rank_text = font_medium.render(f"Rank: {score_rank}", True, "yellow")
            rank_rect = rank_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/5 + 110))
            screen.blit(rank_text, rank_rect)
            
            font_score = pygame.font.Font(None, 36)
            title_text = font_score.render("HIGH SCORES", True, "yellow")
            screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT/2 - 20))
            
            for i, (name, score) in enumerate(high_scores):
                minutes = int(score) // 60
                seconds = int(score) % 60
                score_text = font_score.render(f"{i+1}. {name}: {minutes}:{seconds:02d}", True, "white")
                screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT/2 + 20 + i*30))
            
            if int(time.time() * 2) % 2 == 0:
                font_small = pygame.font.Font(None, 36)
                if is_high_score(game_time, high_scores):
                    restart_text = font_small.render("Press SPACE to save score", True, "green")
                else:
                    restart_text = font_small.render("Press SPACE to play again", True, "white")
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT * 4//5))
                screen.blit(restart_text, restart_rect)
                
                quit_text = font_small.render("Press Q to quit", True, "white")
                quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT * 4//5 + 40))
                screen.blit(quit_text, quit_rect)
        
        elif game_state == ENTER_NAME:
            font_large = pygame.font.Font(None, 60)
            high_score_text = font_large.render("NEW HIGH SCORE!", True, "gold")
            text_rect = high_score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
            screen.blit(high_score_text, text_rect)
            
            font_medium = pygame.font.Font(None, 40)
            minutes = int(game_time) // 60
            seconds = int(game_time) % 60
            time_text = font_medium.render(f"Time Played: {minutes}:{seconds:02d}", True, "white")
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3 + 60))
            screen.blit(time_text, time_rect)
            
            name_prompt = font_medium.render("Enter your name:", True, "white")
            name_prompt_rect = name_prompt.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(name_prompt, name_prompt_rect)
            
            pygame.draw.rect(screen, "white", (SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 + 40, 300, 40), 2)
            name_text = font_medium.render(player_name, True, "white")
            screen.blit(name_text, (SCREEN_WIDTH/2 - 140, SCREEN_HEIGHT/2 + 45))
            
            if int(time.time() * 2) % 2 == 0:
                cursor_x = SCREEN_WIDTH/2 - 140 + name_text.get_width()
                pygame.draw.line(screen, "white", 
                                (cursor_x, SCREEN_HEIGHT/2 + 45), 
                                (cursor_x, SCREEN_HEIGHT/2 + 75), 2)
            
            font_small = pygame.font.Font(None, 30)
            submit_text = font_small.render("Press ENTER to save", True, "green")
            submit_rect = submit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100))
            screen.blit(submit_text, submit_rect)

        pygame.display.flip()

        dt = clock.tick(60) / 1000

if __name__ == "__main__":
    main()
