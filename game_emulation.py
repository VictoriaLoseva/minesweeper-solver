import pygame
from enum import Enum
import random

class Tile:
    def __init__(self) -> None:
        self.covered = True
        self.has_bomb = False
        self.adjacent_bombs = 0
        self.flagged = False

class State(Enum):
    COVERED = 0
    FLAGGED = 1
    REVEALED = 2


class Game_grid:
    def __init__(self, grid_size, num_bombs, tile_draw_size = 32) -> None:
        self.tile_draw_size = tile_draw_size
        self.bombs = num_bombs
        self.size = grid_size
        self.tiles = [ [Tile() for x in range(grid_size)] for y in range(grid_size)]
        self.font = pygame.font.Font(None, 30)
        self.game_started = False

        self.red_flag_sprite = pygame.image.load('img/emoji_u1f6a9.svg')
        self.red_flag_sprite = pygame.transform.scale(self.red_flag_sprite, (25, 25))

        self.bomb_sprite = pygame.image.load('img/emoji_u1f4a3.svg')
        self.bomb_sprite =  pygame.transform.scale(self.bomb_sprite, (25, 25))

        # self.lock_sprite = seguisy80.render('🔒', True, (255, 0, 0))

    def start_game(self, init_row, init_col):
        if init_row == None: init_row = self.size//2
        if init_col == None: init_col = self.size//2

        choices = [i for i in range(self.size**2)]

        #keep the area around the starting square clear
        for dy in range(-1, 2, 1):
            for dx in range(-1, 2, 1):
                d_row = init_row + dy
                d_col = init_col + dx
                if self.in_game_grid(d_row, d_col):
                    site_index = d_row * self.size + d_col
                    choices.remove(site_index)

        # place the bombs
        for _ in range(self.bombs):
            site = random.choice(choices)
            choices.remove(site)
            row = site // self.size
            col = site % self.size
            self.tiles[row][col].has_bomb = True
            self.tiles[row][col].adjacent_bombs = 0
            #incrememt adjacent counts around newly-placed bomb 
            for dy in range(-1, 2, 1):
                for dx in range(-1, 2, 1):
                    d_row = row + dy
                    d_col = col + dx
                    if self.in_game_grid(d_row, d_col):
                        tile = self.tiles[d_row][d_col]
                        if not tile.has_bomb:
                            tile.adjacent_bombs += 1
    
    def in_game_grid(self, row, col) -> bool:
        return row >= 0 and row < self.size and col >= 0 and col < self.size

    def draw(self, screen):
        dsize = self.tile_draw_size
        for row in range(self.size):
            for col in range(self.size):
                tile = self.tiles[row][col]
                if not tile.covered: 
                    pygame.draw.rect(
                            screen, 
                            (150, 150, 150), 
                            (col * dsize, row * dsize, dsize, dsize),
                    )
                    if tile.has_bomb:  
                        surface_x, surface_y = self.bomb_sprite.get_size() 
                        screen.blit(self.bomb_sprite, (col * dsize + dsize//2 - surface_x//2, row * dsize + dsize//2 - surface_y//2))
                else:
                    pygame.draw.rect(
                                screen, 
                                (100, 100, 100), 
                                (col * dsize, row * dsize, dsize, dsize),
                        )
                pygame.draw.rect(
                    screen, 
                    (0, 0, 0), 
                    (col * dsize, row * dsize, dsize, dsize),
                    width=1
                )

                if tile.flagged:
                    surface_x, surface_y = self.red_flag_sprite.get_size() 
                    screen.blit(self.red_flag_sprite, (col * dsize + dsize//2 - surface_x//2, row * dsize + dsize//2 - surface_y//2))

                if tile.covered or tile.adjacent_bombs == 0: continue
                text_surface = self.font.render(str(tile.adjacent_bombs), True, (255, 255, 255))
                surface_x, surface_y = text_surface.get_size() 
                screen.blit(text_surface, (col * dsize + dsize//2 - surface_x//2, row * dsize + dsize//2 - surface_y//2))
    
    def uncover_tile(self, row, col):
        if not self.in_game_grid(row, col): return
        if not self.game_started:
            self.start_game(row, col)
            self.game_started = True
        
        tile = self.tiles[row][col]
        if not tile.covered: return
        tile.covered = False
        tile.flagged = False
        if tile.adjacent_bombs != 0 or tile.has_bomb: return 

        #if a tile has 0 adjacent_bombs uncover it's neighbors
        for dy in range(-1, 2, 1):
            for dx in range(-1, 2, 1):
                d_row = row + dy
                d_col = col + dx
                if self.in_game_grid(d_row, d_col):
                    self.uncover_tile(d_row, d_col)
    
    def flag_tile(self, row, col, flagged=None):
        if not self.in_game_grid(row, col): return
        tile = self.tiles[row][col]
        if tile.covered:
            tile.flagged = flagged if flagged != None else not tile.flagged

    def mouse_to_row_col(self, mouse_x, mouse_y = None):
        if mouse_y == None:
            return (mouse_x[1]//self.tile_draw_size, mouse_x[0]//self.tile_draw_size)
        return (mouse_y//self.tile_draw_size, mouse_x//self.tile_draw_size)

