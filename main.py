import pygame
from game_emulation import Game_grid
from minesweeper_solver import Solver 

def proccess_events(game_grid):
    global screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_row_col = game_grid.mouse_to_row_col(pygame.mouse.get_pos())
            if event.button == 1:
                game_grid.uncover_tile(mouse_row_col[0], mouse_row_col[1])
            if event.button == 3:
                game_grid.flag_tile(mouse_row_col[0], mouse_row_col[1])
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game_grid = Game_grid(game_grid.size, game_grid.bombs)
                game_grid.draw(screen)
                print(game_grid)
            if event.key == pygame.K_s:
                solver = Solver(game_grid, screen)
                solver.launch(game_grid, screen)
    return game_grid

pygame.init()
game_grid = Game_grid(18, 60)
print(game_grid)
screen = pygame.display.set_mode([18*32, 18*32])


running = True
while game_grid is not None:
    # Fill the background with white
    screen.fill((255, 255, 255))

    #Draw game grid
    game_grid.draw(screen)

    # Did the user click the window close button?
    game_grid = proccess_events(game_grid)

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()