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

    #extracts state from the game emulator to the solver tiles passed into it
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

    def search_for_determinism(self, solver_grid:list[list[Solver_Tile]], render = False):
        actions = []
        for row in range(len(solver_grid)):
            for col in range(len(solver_grid[row])):
                tile = solver_grid[row][col]
                tile_actions = []

                if(tile.covered() or tile.flagged() or tile.adjacent_bombs == 0): 
                    #actions.append((tile, tile_actions))
                    continue

                covered_neighbors = tile.get_neighbors_of_state(State.COVERED)
                flagged_neighbors = tile.get_neighbors_of_state(State.FLAGGED)

                #if all adjacent covered tiles guaranteed to be bombs, flag them
                if len(covered_neighbors) + len(flagged_neighbors) == tile.adjacent_bombs:
                    for neighbor in covered_neighbors: tile_actions += [(State.FLAGGED, neighbor)]
                    
                #if all adjacent bombs accounted for, reveal unflagged tiles.
                if len(flagged_neighbors) == tile.adjacent_bombs and len(covered_neighbors) > 0:
                    for neighbor in covered_neighbors: tile_actions += [(State.REVEALED, neighbor)]
                if tile_actions: actions.append((tile, tile_actions))
                
        return actions
    
    def run_simulation(self, solver_grid:list[list[Solver_Tile]], combination:list[Solver_Tile], render = False):
        print("running sim")
        actions = []
        sim_grid = [[Solver_Tile() for col in range(self.game_grid.size) ] for row in range(self.game_grid.size)] #copy.copy(solver_grid)
        self.extract_state(sim_grid)
        #sim_grid = copy.copy(game_grid)

        for neighbor in combination:
            print(f"    flagging {neighbor.row}, {neighbor.col}")
            self.push_overlay(neighbor.row, neighbor.col, (255, 255, 0))
            sim_grid[neighbor.row][neighbor.col].state = State.FLAGGED
            actions += [(State.FLAGGED, (neighbor.row, neighbor.col))]
            # neighbor.state = State.FLAGGED
        
        while True: 
            new_actions = self.search_for_determinism(sim_grid)
            
            if not new_actions: break
            #unpack the format that search for determinism returns
            new_actions = [(action, tile) for _, tile_actions in new_actions for action, tile in tile_actions]
            # print([(action, (tile.row, tile.col)) for action, tile in new_actions])
            for action, acted_on_tile in new_actions:
                        acted_on_tile.state = action
            if not self.is_sat(sim_grid): return "unsat"
            # self.extract_state(sim_grid)
            actions += [(action, (tile.row, tile.col)) for action, tile in new_actions]
        self.wait_for_input(self.screen, sim_grid)

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

    def make_action_set(self, action_pairs):
        action_set = set()
        for tile, actions in action_pairs:
            for action in actions: action_set.add(action)
        return action_set

    def find_50_50_tiles(self, solver_grid:list[list[Solver_Tile]]) -> list[Solver_Tile]:
        tiles = []
        for row in range(len(solver_grid)):
            for col in range(len(solver_grid[row])):
                tile = solver_grid[row][col]

                if(tile.covered() or tile.flagged() or tile.adjacent_bombs == 0): 
                    continue

                flagged_neighbors = tile.get_neighbors_of_state(State.FLAGGED)
                covered_neighbors = tile.get_neighbors_of_state(State.COVERED)
                if (tile.adjacent_bombs - len(flagged_neighbors)) == 1 and len(covered_neighbors) == 2:
                    tiles.append(tile)
        return tiles
    
    def find_unsolved(self, solver_grid:list[list[Solver_Tile]]) -> list[Solver_Tile]:
        tiles = []
        for row in range(len(solver_grid)):
            for col in range(len(solver_grid[row])):
                tile = solver_grid[row][col]

                if(tile.covered() or tile.flagged() or tile.adjacent_bombs == 0): 
                    continue

                flagged_neighbors = tile.get_neighbors_of_state(State.FLAGGED)
                covered_neighbors = tile.get_neighbors_of_state(State.COVERED)
                if (tile.adjacent_bombs - len(flagged_neighbors)) >=1:
                    tiles.append(tile)
        return tiles

    #deterministic choices can be applied directly to the game board, so the game_grid object is passed in
    def solve_all_determinism(self, screen, solver_grid, game_grid=None): 
        change_made = True
        while change_made:
            change_made = False
            
            tile_action_pairs = self.search_for_determinism(solver_grid)
            for tile, actions in tile_action_pairs:
                # self.push_overlay(tile.row, tile.col, (255, 255, 150))
                #self.render(5)
                if len(actions) == 0: 
                    self.clear_overlays()
                    continue

                for action, acted_on_tile in actions:
                    change_made = True
                    acted_on_tile.state = action
                    if game_grid != None: 
                        if action == State.FLAGGED:
                            game_grid.flag_tile(acted_on_tile.row, acted_on_tile.col, True)
                            #self.push_and_render_overlay(acted_on_tile.row, acted_on_tile.col, (255, 0, 0), 50)
                        if action == State.REVEALED:
                            game_grid.uncover_tile(acted_on_tile.row, acted_on_tile.col)
                            #self.push_and_render_overlay(acted_on_tile.row, acted_on_tile.col, (0, 255, 0), 50)
                
                self.clear_overlays()
            self.extract_state(solver_grid)
        self.render(screen, solver_grid, 10)

    def find_guaranteed_actions(self, screen, solver_grid, source_tile):
        covered_tiles = source_tile.get_neighbors_of_state(State.COVERED)
        flagged_neighbors = source_tile.get_neighbors_of_state(State.FLAGGED)
        num_unflagged = (source_tile.adjacent_bombs - len(flagged_neighbors))

        guaranteed_actions = set()
        returned_actions = []

        first = True
        possible_combinations_to_cover = combinations(covered_tiles, num_unflagged)
        for combination in possible_combinations_to_cover:
            #run sim with choice of flagged neighbors
            actions = self.run_simulation(solver_grid, combination)

            #if unfeasable choice, continue
            if actions == "unsat": 
                print("found unsat configuration")
                self.wait_for_input(screen, self.tiles)
                continue

            actions_set = set()
            for action in actions: actions_set.add(action)
            print("    consequent actions:")
            for action, (row, col) in actions_set:
                print("        ", action, f"({row}, {col})")

            returned_actions += [set(actions)]
            
            #initialize the list or do the intersection 
            # if first:
            #     guaranteed_actions = actions_set
            #     first = False
            # guaranteed_actions = guaranteed_actions.intersection(actions_set)
            self.clear_overlays()

        #convert the guaranteed actions into grid coordinates
        guaranteed_actions = [(action, solver_grid[row][col]) for action, (row, col) in set.intersection(*returned_actions)]
        # guaranteed_actions = [(action, solver_grid[row][col]) for action, tile in guaranteed_actions]
        print(f"    guaranteed actions  : {[(action, (tile.row, tile.col)) for action, tile in guaranteed_actions]}")
        return guaranteed_actions 


# note to self: make an action queue for game_grid object that takes in either debug actions or game actions
    def launch(self, game_grid, screen): 
        #solve all low-hanging fruit
        iters = 0
        solved = False
        change_made = False
        while not solved:
            
            self.solve_all_determinism(screen, self.tiles, game_grid)

            # potential_tiles = self.find_50_50_tiles(self.tiles)
            potential_tiles = self.find_unsolved(self.tiles)
            print("50/50: ", [(tile.row, tile.col) for tile in potential_tiles])
            for tile in potential_tiles:
                print(f"looking at actions for 50/50 tile ({tile.row}, {tile.col}):")
                self.push_overlay(tile.row, tile.col, (255, 0, 0))
                self.wait_for_input(screen, self.tiles)

                guaranteed_actions = self.find_guaranteed_actions(screen, self.tiles, tile)
                self.clear_overlays()


                if len(guaranteed_actions) == 0: 
                    print("no guaranteed actions")
                    continue
                change_made = True
                print("running guaranteed actions...")
                print("intersect:")
                for action, tile in guaranteed_actions:
                    print("  ", action, f"({tile.row}, {tile.col})")
                for action, acted_on_tile in guaranteed_actions:
                        change_made = True
                        acted_on_tile.state = action
                        if action == State.FLAGGED:
                            game_grid.flag_tile(acted_on_tile.row, acted_on_tile.col, True)
                            self.push_and_render_overlay(screen, self.tiles, acted_on_tile.row, acted_on_tile.col, (255, 0, 0), 1000)
                        if action == State.REVEALED:
                            game_grid.uncover_tile(acted_on_tile.row, acted_on_tile.col)
                            self.push_and_render_overlay(screen, self.tiles, acted_on_tile.row, acted_on_tile.col, (0, 255, 0), 1000)
                self.extract_state(self.tiles)
            if not change_made:
                solved = True
                    


    def push_overlay(self, row, col, color):
        self.overlays.append(self.Overlay(row, col, color))

    def pop_overlay(self):
        self.overlays.pop()

    def push_and_render_overlay(self, screen, solver_grid, row, col, color, delay):
        self.overlays.append(self.Overlay(row, col, color))
        self.draw(screen, solver_grid)
        self.render(screen, solver_grid, delay)

    def clear_overlays(self):
        self.overlays = []

    def draw(self, screen, solver_grid):
        self.screen.fill((255, 255, 255))
        self.game_grid.draw(self.screen)
        dsize = self.game_grid.tile_draw_size

        for overlay in self.overlays:
            offset = 2
            rect = (overlay.col * dsize + offset, overlay.row * dsize + offset, dsize - offset * 2, dsize - offset * 2)
            pygame.draw.rect(screen, overlay.color, rect, width=2)
            pygame.time.wait(overlay.delay)

        for row in range(self.game_grid.size):
            for col in range(self.game_grid.size):
                tile = solver_grid[row][col]
                text_surface = self.font.render(".", True, (100, 0, 0))
                if tile.flagged(): 
                    text_surface = self.font.render("f", True, (100, 0, 0))
                    # surface_w, surface_h = text_surface.get_size() 
                elif tile.revealed(): 
                    text_surface = self.font.render("r", True, (0, 100, 0))
                self.screen.blit(text_surface, (col * dsize, row * dsize))

    def render(self, screen, solver_grid, wait_time = 0):
        self.draw(screen, solver_grid)
        pygame.display.flip()
        #proccess_events(self.game_grid)
        pygame.time.wait(wait_time)
    
    def wait_for_input(self, screen, solver_grid, clear_overlays = False):
        reee = True
        self.render(screen, solver_grid)
        while (reee):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                    reee = False
                    if clear_overlays: self.clear_overlays()


        
