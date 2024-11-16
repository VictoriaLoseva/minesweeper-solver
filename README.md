<p align="center">
   <img src="game_recording.gif">
</p>

# Setup
The only depdency is ```pygame```. Written with v2.5.2

# How to run 
This command will launch the minesweeper emulation. 

``` python main.py ``` 

# Interacting 
You can play on your own by using right click to place a flag and left click to uncover a tile.

Other commands: 
* 's' - solver 'shows its work' for one iteration on the board.
* 'S' - solver solves immediately does one iteration and shows its work for one solvable square. 

The solver will highlight the source tiles for easy choices in red, difficult choices in yellow, and the choices it makes in green. 

Unfortunately, minesweeper is not an entirely deterministic game and some choices, without hints, are entirely up to luck! If 's'/'S' is pressed and nothing happens, the solver cannot make any further decisions. 

# Internals 
Strategies used in solver, in order of application: 
* Arc consistency (regular minesweeper gameplay)
* Trying different flag configurations for unsolved squares to find invariant actions (no recursion)
* End-game logic: are there enough bombs for a particular placement? (coming soon)

# Next features
* Make the graphics nicer! 
* Add new actions: hints or launch autosolver
    * Make the window closeable during autosolver 

