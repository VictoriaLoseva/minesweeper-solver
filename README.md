# How to run 
This command will launch the minesweeper emulation. 
``` python main.py ``` 

You can play on your own by using right click to place a flag and left click to uncover a tile.
You can also launch launch the solver with 's'. The solver will make all deterministic choices on the board. 
Unfortunately, minesweeper is not an entirely deterministic game and some choices, without hints, are entirely up to luck! 
The solver will not proceed at that point. 

# Internals 
Strategies used in solver, in order of application: 
* Arc consistency (regular minesweeper gameplay)
* Trying different flag configurations for unsolved squares to find invariant actions (no recursion)
* End-game logic: are there enough bombs for a particular placement? (coming soon)
