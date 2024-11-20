import pygame
from game_emulation import Game_grid
from minesweeper_solver import Solver 

with open("logs/006.txt", 'r') as f:
    size = int(f.readline())
    num_bombs = int(f.readline())
    last_tile = eval(f.readline())
    load = eval(f.readline())

# Set up game
pygame.init()
screen = pygame.display.set_mode([size*32, size*32])
pygame.display.set_caption("minesweeper_test")


game_grid = Game_grid(size, num_bombs, load=load)

while game_grid is not None:
    # Fill the background with white
    screen.fill((255, 255, 255))

    #Draw game grid
    game_grid.draw(screen)

    # Did the user click the window close button?
    # game_grid = proccess_events(game_grid)

    # Flip the display
    pygame.display.flip()

    #Take a screnshot

# Done! Time to quit.
pygame.quit()