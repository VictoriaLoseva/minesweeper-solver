import pygame
from itertools import combinations
import copy
from game_emulation import State, Game_grid

class Solver_Tile:
    def __init__(self) -> None:
        self.state = State.COVERED
        self.flagged_bombs = 0
        self.adjacent_bombs = 0
        self.neighbors = []
        self.locked = False
        self.row = -1
        self.col = -1

    def get_neighbors_of_state(self, state):
        return [neighbor for neighbor in self.neighbors if neighbor.state == state]

    def covered(self): 
        return self.state == State.COVERED
    
    def flagged(self):
        return self.state == State.FLAGGED

    def revealed(self):
        return self.state == State.REVEALED
    

class Solver:
    class Overlay:
        def __init__(self, row, col, color, delay = 0) -> None:
            self.row = row
            self.col = col
            self.color = color
            self.delay = delay
    
    def __init__(self, game_grid:Game_grid, screen) -> None:
        self.screen = screen
        self.font = pygame.font.Font(None, 20)
        self.game_grid = game_grid
        # First move always in the center
        if not game_grid.game_started:
            game_grid.uncover_tile(game_grid.size //2 , game_grid.size // 2)
        self.tiles = [[Solver_Tile() for col in range(game_grid.size) ] for row in range(game_grid.size)]
        self.extract_state(self.tiles)
        self.overlays = []

    def extract_state(self, grid:list[list[Solver_Tile]]):
        for row in range(self.game_grid.size):
            for col in range(self.game_grid.size):
                my_tile = grid[row][col]
                other_tile = self.game_grid.tiles[row][col]
                if other_tile.flagged:
                    my_tile.state = State.FLAGGED
                elif not other_tile.covered:
                    my_tile.state = State.REVEALED
                else:
                    my_tile.state = State.COVERED
                if my_tile.revealed():
                    my_tile.adjacent_bombs = other_tile.adjacent_bombs
                my_tile.row = row
                my_tile.col = col
                if len(my_tile.neighbors) != 0: continue #only add neighbors once
                for dy in range(-1, 2, 1):
                    for dx in range(-1, 2, 1):
                        d_row = row + dy
                        d_col = col + dx
                        if not self.game_grid.in_game_grid(d_row, d_col) or (d_row == row and d_col == col): continue
                        my_tile.neighbors.append(grid[d_row][d_col])

    def search_for_determinism(self, grid:list[list[Solver_Tile]], render = False):
        actions = []
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                tile = grid[row][col]
                tile_actions = []

                if(tile.covered() or tile.flagged() or tile.adjacent_bombs == 0): 
                    #actions.append((tile, tile_actions))
                    continue

                covered_neighbors = tile.get_neighbors_of_state(State.COVERED)
                flagged_neighbors = tile.get_neighbors_of_state(State.FLAGGED)

                #all adjacent covered tiles guaranteed to be bombs, flag them
                if len(covered_neighbors) + len(flagged_neighbors) == tile.adjacent_bombs:
                    for neighbor in covered_neighbors: tile_actions += [(State.FLAGGED, neighbor)]
                    
                #all bombs accounted for, reveal unflagged tiles.
                if len(flagged_neighbors) == tile.adjacent_bombs and len(covered_neighbors) > 0:
                    for neighbor in covered_neighbors: tile_actions += [(State.REVEALED, neighbor)]
                if tile_actions: actions.append((tile, tile_actions))
                
        return actions
    
    def run_simulation(self, grid:list[list[Solver_Tile]], render = False):
        print("running sim")
        actions = []
        sim_grid = copy.copy(grid)
        #sim_grid = copy.copy(game_grid)
        while True: 
            new_actions = self.search_for_determinism(sim_grid)
            print(new_actions)
            if not new_actions: break
            #unpack the format that search for determinism returns
            new_actions = [(tile, action) for _, tile_actions in new_actions for tile, action in tile_actions]
            print(new_actions)
            for action, acted_on_tile in new_actions:
                        acted_on_tile.state = action
            if not self.is_sat(sim_grid): return "unsat"

            actions += new_actions

        return actions


    def is_sat(self, grid:list[list[Solver_Tile]]):
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                tile = grid[row][col]

                if(tile.covered() or tile.flagged() or tile.adjacent_bombs == 0): 
                    continue

                flagged_neighbors = tile.get_neighbors_of_state(State.FLAGGED)
                
                if len(flagged_neighbors) > tile.adjacent_bombs:
                    return False
                
        return True

    # The ob
    def make_action_set(self, action_pairs):
        action_set = set()
        for tile, actions in action_pairs:
            for action in actions: action_set.add(action)
        return action_set

    def find_50_50_tiles(self, grid:list[list[Solver_Tile]]) -> list[Solver_Tile]:
        tiles = []
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                tile = grid[row][col]

                if(tile.covered() or tile.flagged() or tile.adjacent_bombs == 0): 
                    continue

                flagged_neighbors = tile.get_neighbors_of_state(State.FLAGGED)
                if (tile.adjacent_bombs - len(flagged_neighbors)) >= 1:
                    tiles.append(tile)
                
        return tiles
    

    def push_overlay(self, row, col, color):
        self.overlays.append(self.Overlay(row, col, color))

    def pop_overlay(self):
        self.overlays.pop()

    def push_and_render_overlay(self, row, col, color, delay):
        self.overlays.append(self.Overlay(row, col, color))
        self.draw()
        self.render(delay)

    def clear_overlays(self):
        self.overlays = []

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.game_grid.draw(self.screen)
        dsize = self.game_grid.tile_draw_size
        for row in range(self.game_grid.size):
            for col in range(self.game_grid.size):
                tile = self.tiles[row][col]
                if not tile.flagged(): continue 
                text_surface = self.font.render("f", True, (100, 0, 0))
                surface_w, surface_h = text_surface.get_size() 
                self.screen.blit(text_surface, (col * dsize, row * dsize))
        for overlay in self.overlays:
            offset = 2
            rect = (overlay.col * dsize + offset, overlay.row * dsize + offset, dsize - offset * 2, dsize - offset * 2)
            pygame.draw.rect(screen, overlay.color, rect, width=2)
            pygame.time.wait(overlay.delay)

    def render(self, wait_time = 0):
        self.draw()
        pygame.display.flip()
        #proccess_events(self.game_grid)
        pygame.time.wait(wait_time)
    
    def wait_for_input(self, clear_overlays = False):
        reee = True
        while (reee):
            self.render()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                    reee = False
                    if clear_overlays: self.clear_overlays()

    def launch(self): 
        #solve all low-hanging fruit
        iters = 0
        solved = False
        while not solved:
            change_made = True
            while change_made:
                print("doing iter:", iters)
                iters += 1
                change_made = False
                
                tile_action_pairs = self.search_for_determinism(self.tiles)
                for tile, actions in tile_action_pairs:
                    self.push_overlay(tile.row, tile.col, (255, 255, 150))
                    #self.render(5)
                    if len(actions) == 0: 
                        self.clear_overlays()
                        continue

                    for action, acted_on_tile in actions:
                        change_made = True
                        acted_on_tile.state = action
                        if action == State.FLAGGED:
                            game_grid.flag_tile(acted_on_tile.row, acted_on_tile.col, True)
                            #self.push_and_render_overlay(acted_on_tile.row, acted_on_tile.col, (255, 0, 0), 50)
                        if action == State.REVEALED:
                            game_grid.uncover_tile(acted_on_tile.row, acted_on_tile.col)
                            #self.push_and_render_overlay(acted_on_tile.row, acted_on_tile.col, (0, 255, 0), 50)
                    
                    self.clear_overlays()
                self.extract_state(self.tiles)
            self.render(10)
            potential_tiles = self.find_50_50_tiles(self.tiles)
            for tile in potential_tiles:
                print(f"looking at actions for ({tile.row}, {tile.col}):")
                self.push_overlay(tile.row, tile.col, (255, 0, 0))

                covered_tiles = tile.get_neighbors_of_state(State.COVERED)
                flagged_neighbors = tile.get_neighbors_of_state(State.FLAGGED)
                num_unflagged = (tile.adjacent_bombs - len(flagged_neighbors))

                guaranteed_actions = set()

                first = True
                possible_combinations_to_cover = combinations(covered_tiles, num_unflagged)
                for combination in possible_combinations_to_cover:
                    #cover each neighbor
                    for neighbor in combination:
                        print(f"  flagging ({tile.row}, {tile.col})")
                        self.push_overlay(neighbor.row, neighbor.col, (255, 255, 0))
                        neighbor.state = State.FLAGGED
                        
                    #run search for determinism
                    #actions_set = self.make_action_set(self.search_for_determinism(self.tiles))
                    actions = self.run_simulation(self.tiles)
                    if actions == "unsat": 
                        print("found unsat configuration")
                        self.wait_for_input()
                        continue
                    actions_set = set()
                    for action in actions: actions_set.add(action)
                    for action, tile in actions_set:
                        print("    ", action, f"({tile.row}, {tile.col})")
                    #do the intersection thing
                    if first:
                        guaranteed_actions = actions_set
                        first = False
                    guaranteed_actions = guaranteed_actions.intersection(actions_set)
                    #uncover tiles
                    self.wait_for_input(False)
                    for neighbor in combination: 
                        neighbor.state = State.COVERED
                        self.pop_overlay()
                self.clear_overlays()
                # for covered_tile in covered_tiles:
                #     covered_tile.state = State.FLAGGED
                #     self.push_overlay(covered_tile.row, covered_tile.col, (255, 255, 0))
                #     actions_set = self.make_action_set(self.search_for_determinism(self.tiles))
                #     print(f"looking at actions for ({covered_tile.row}, {covered_tile.col}):")
                #     for action, tile in actions_set:
                #         print("  ", action, f"({tile.row}, {tile.col})")
                #     if first:
                #         guaranteed_actions = actions_set
                #         first = False
                #     guaranteed_actions = guaranteed_actions.intersection(actions_set)
                #     covered_tile.state = State.COVERED

                #compare action tile pairs, if any of them are equal, modify state  
                print("intersect:")
                for action, tile in guaranteed_actions:
                    print("  ", action, f"({tile.row}, {tile.col})")


                if len(guaranteed_actions) != 0: print("running guaranteed actions...")
                for action, acted_on_tile in guaranteed_actions:
                        change_made = True
                        acted_on_tile.state = action
                        if action == State.FLAGGED:
                            game_grid.flag_tile(acted_on_tile.row, acted_on_tile.col, True)
                            self.push_and_render_overlay(acted_on_tile.row, acted_on_tile.col, (255, 0, 0), 1000)
                        if action == State.REVEALED:
                            game_grid.uncover_tile(acted_on_tile.row, acted_on_tile.col)
                            self.push_and_render_overlay(acted_on_tile.row, acted_on_tile.col, (0, 255, 0), 1000)
                if change_made: 
                    break
            if not change_made:
                solved = True
                    

        #now need to find unsat solutions 
        
        

def proccess_events(game_grid):
    global screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_row_col = game_grid.mouse_to_row_col(pygame.mouse.get_pos())
            if event.button == 1:
                game_grid.uncover_tile(mouse_row_col[0], mouse_row_col[1])
            if event.button == 3:
                game_grid.flag_tile(mouse_row_col[0], mouse_row_col[1])
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game_grid = Game_grid(game_grid.size, game_grid.bombs)
            if event.key == pygame.K_s:
                solver = Solver(game_grid, screen)
                solver.launch()
    return True

pygame.init()
game_grid = Game_grid(18, 60)
screen = pygame.display.set_mode([18*32, 18*32])

#solver.search_for_determinism()
running = True
while running:
    # Did the user click the window close button?
    running = proccess_events(game_grid)

    # Fill the background with white
    screen.fill((255, 255, 255))

    game_grid.draw(screen)

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()