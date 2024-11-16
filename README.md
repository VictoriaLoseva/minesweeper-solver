# Setup
The only depdency is ```pygame```. Written with v2.5.2

# How to run 
This command will launch the minesweeper emulation. 
``` python main.py ``` 

# Interacting 
You can play on your own by using right click to place a flag and left click to uncover a tile.

You can also launch launch the solver with 's'. It will complete one iteration of either making all the 'obvious' choices, or will make a choice on one of the unsolved tiles. If it is making a choice, it will highlight the source tile in red, and the resulting actions in green. 

Unfortunately, minesweeper is not an entirely deterministic game and some choices, without hints, are entirely up to luck! If 's' is pressed and nothing happens, the solver cannot make any further decisions. 

# Internals 
Strategies used in solver, in order of application: 
* Arc consistency (regular minesweeper gameplay)
* Trying different flag configurations for unsolved squares to find invariant actions (no recursion)
* End-game logic: are there enough bombs for a particular placement? (coming soon)

# Next features
* Make the graphics nicer! 
* Add new actions: hints or launch autosolver
    * Make the window closeable during autosolver 

