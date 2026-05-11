# Maze Construction (Stack-based DFS "Mouse")
1. All walls start out intact
2. Place the mouse at a random cell and mark it visited
3. Check all 4 neighbours of the current cell for visited/unvisited status
4. Select an unvisited neighbour randomly, move into it and eat the wall between
5. Unselected unvisited neighbours are pushed onto the stack
6. If no such neighbours remain, pop a cell off the stack and backtrack to it
7. Repeat steps 3-6 until the stack runs out – maze created

This maze uses two 2D arrays for storing wall data.

northWall[R][C] – this array stores the wall above each cell; if the value is equal to 1, the wall is not destroyed. Otherwise, the wall is eaten.
eastWall[R][C] – this array stores the wall on the right of each cell; follows the same principle as above.

Row number 0 of northWall is a phantom row, which forms the bottom border of the maze. Column number 0 of eastWall is a phantom column, which forms the left border of the maze.
Amiel Abebe
UGR/5619/16
Section:1
