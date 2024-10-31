# How to run 
This command will launch the minesweeper emulation. 
``` python minesweeper_solver.py ``` 

You can play on your own by using right click to place a flag and left click to uncover a tile.
You can also launch launch the solver with 's'. The solver will make all deterministic choices on the board. 
Unfortunately, minesweeper is not an entirely deterministic game and some choices, without hints, are entirely up to luck! The solver will not proceed at that point. 

# Internals 
Strategies used in solver, in order of application: 
* Arc consistency (regular minesweeper gameplay)
* Pattern matching ('121' pattern for example)
* End-game logic: are there enough bombs for a particular placement? 
