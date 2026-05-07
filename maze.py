import pygame
import random
import sys

ROWS       = 15
COLS       = 15
CELL_SIZE  = 40 
MARGIN     = 40
GEN_DELAY  = 20
SOLVE_DELAY= 30   

BG_COLOR   = (245, 245, 245)
BLACK      = (30,  30,  30)
LIGHT_BLUE = (214, 234, 248)  
RED        = (231, 76,  60)    
BLUE       = (52,  152, 219)  
GREEN      = (46,  204, 113)  
ORANGE     = (243, 156, 18)   
PURPLE     = (155, 89,  182)  


class Maze:
    def __init__(self, rows, cols):
        self.R = rows
        self.C = cols
        # northWall[r][c] = 1 means the TOP wall of cell (r,c) is intact
        # northWall[r][c] = 0 means the wall has been eaten through
        # Row 0 is a phantom row whose north walls form the BOTTOM border
        self.northWall = [[1] * cols for _ in range(rows + 1)]
        # eastWall[r][c] = 1 means the RIGHT wall of cell (r,c) is intact
        # eastWall[r][c] = 0 means the wall has been eaten through
        # Column 0 is a phantom column whose east walls form the LEFT border
        self.eastWall  = [[1] * (cols + 1) for _ in range(rows)]

    def top_wall(self, r, c):    return self.northWall[r][c] == 1
    def bottom_wall(self, r, c): return self.northWall[r - 1][c] == 1 if r > 0 else self.northWall[0][c] == 1
    def right_wall(self, r, c):  return self.eastWall[r][c + 1] == 1
    def left_wall(self, r, c):   return self.eastWall[r][c] == 1

    def remove_top(self, r, c):    self.northWall[r][c] = 0
    def remove_bottom(self, r, c):
        if r > 0: self.northWall[r - 1][c] = 0
        else:     self.northWall[0][c] = 0
    def remove_right(self, r, c):  self.eastWall[r][c + 1] = 0
    def remove_left(self, r, c):   self.eastWall[r][c] = 0

    def can_move(self, r, c, direction):
        if direction == 'N': return r + 1 < self.R and not self.top_wall(r, c)
        if direction == 'S': return r - 1 >= 0     and not self.bottom_wall(r, c)
        if direction == 'E': return c + 1 < self.C and not self.right_wall(r, c)
        if direction == 'W': return c - 1 >= 0     and not self.left_wall(r, c)
        return False


class MazeGenerator:
    # Stack-based DFS mouse that eats through walls
    def __init__(self, maze):
        self.maze    = maze
        self.visited = [[False] * maze.C for _ in range(maze.R)]
        self.stack   = []
        self.done    = False
        self.current = (0, 0)

        sr = random.randint(0, maze.R - 1)
        sc = random.randint(0, maze.C - 1)
        self.visited[sr][sc] = True
        self.stack.append((sr, sc))
        self.current = (sr, sc)

    def step(self):
        if not self.stack:
            self.done = True
            return

        r, c = self.stack[-1]
        self.current = (r, c)

        neighbours = []
        if r + 1 < self.maze.R and not self.visited[r + 1][c]: neighbours.append((r+1, c, 'N'))
        if r - 1 >= 0          and not self.visited[r - 1][c]: neighbours.append((r-1, c, 'S'))
        if c + 1 < self.maze.C and not self.visited[r][c + 1]: neighbours.append((r, c+1, 'E'))
        if c - 1 >= 0          and not self.visited[r][c - 1]: neighbours.append((r, c-1, 'W'))

        if not neighbours:
            self.stack.pop()
            return

        nr, nc, direction = random.choice(neighbours)

        if direction == 'N': self.maze.remove_top(r, c)
        elif direction == 'S': self.maze.remove_bottom(r, c)
        elif direction == 'E': self.maze.remove_right(r, c)
        elif direction == 'W': self.maze.remove_left(r, c)

        self.visited[nr][nc] = True
        self.stack.append((nr, nc))


class MazeSolver:
    DIRECTIONS = ['N', 'S', 'E', 'W']

    def __init__(self, maze, start, end):
        self.maze      = maze
        self.start     = start
        self.end       = end
        self.stack     = [start]
        self.visited   = [[False] * maze.C for _ in range(maze.R)]
        self.visited[start[0]][start[1]] = True
        self.dead_ends = set()
        self.solution  = []
        self.done      = False
        self.current   = start

    def step(self):
        if not self.stack:
            self.done = True
            return

        r, c = self.stack[-1]
        self.current = (r, c)

        if (r, c) == self.end:
            self.solution = list(self.stack)
            self.done = True
            return

        dirs = self.DIRECTIONS[:]
        random.shuffle(dirs)

        moved = False
        for direction in dirs:
            if   direction == 'N': nr, nc = r + 1, c
            elif direction == 'S': nr, nc = r - 1, c
            elif direction == 'E': nr, nc = r, c + 1
            else:                  nr, nc = r, c - 1

            if not self.maze.can_move(r, c, direction): continue
            if self.visited[nr][nc]: continue

            self.visited[nr][nc] = True
            self.stack.append((nr, nc))
            moved = True
            break

        if not moved:
            self.dead_ends.add((r, c))
            self.stack.pop()


class Renderer:
    def __init__(self, maze, screen):
        self.maze   = maze
        self.screen = screen

    def cell_rect(self, r, c):
        x = MARGIN + c * CELL_SIZE
        y = MARGIN + (self.maze.R - 1 - r) * CELL_SIZE
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def fill_cell(self, r, c, color):
        pygame.draw.rect(self.screen, color, self.cell_rect(r, c))

    def draw_dot(self, r, c, color):
        rect   = self.cell_rect(r, c)
        radius = max(4, CELL_SIZE // 4)
        pygame.draw.circle(self.screen, color, rect.center, radius)

    def draw_walls(self):
        R, C   = self.maze.R, self.maze.C
        lw     = max(2, CELL_SIZE // 10)

        for r in range(R):
            vr = R - 1 - r
            for c in range(C):
                x = MARGIN + c * CELL_SIZE
                y = MARGIN + vr * CELL_SIZE
                if self.maze.northWall[r][c]:
                    pygame.draw.line(self.screen, BLACK, (x, y), (x + CELL_SIZE, y), lw)
                if self.maze.eastWall[r][c + 1]:
                    pygame.draw.line(self.screen, BLACK, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), lw)

        for c in range(C):
            if self.maze.northWall[0][c]:
                x = MARGIN + c * CELL_SIZE
                y = MARGIN + R * CELL_SIZE
                pygame.draw.line(self.screen, BLACK, (x, y), (x + CELL_SIZE, y), lw)

        for r in range(R):
            vr = R - 1 - r
            if self.maze.eastWall[r][0]:
                x = MARGIN
                y = MARGIN + vr * CELL_SIZE
                pygame.draw.line(self.screen, BLACK, (x, y), (x, y + CELL_SIZE), lw)

    def draw_all(self, gen=None, solver=None):
        self.screen.fill(BG_COLOR)

        if gen is not None:
            for r in range(self.maze.R):
                for c in range(self.maze.C):
                    if gen.visited[r][c]:
                        self.fill_cell(r, c, LIGHT_BLUE)
            if not gen.done:
                self.fill_cell(*gen.current, RED)

        if solver is not None:
            for (r, c) in solver.dead_ends:
                self.fill_cell(r, c, BLUE)
            for (r, c) in solver.stack:
                self.fill_cell(r, c, GREEN)
            if solver.solution:
                for (r, c) in solver.solution:
                    self.fill_cell(r, c, GREEN)
            if not solver.done:
                self.fill_cell(*solver.current, RED)

        self.draw_walls()
        self.draw_dot(0, 0, ORANGE)                           
        self.draw_dot(self.maze.R - 1, self.maze.C - 1, PURPLE) 


def main():
    pygame.init()

    win_w = COLS * CELL_SIZE + 2 * MARGIN
    win_h = ROWS * CELL_SIZE + 2 * MARGIN + 50
    screen = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Building and Running Mazes")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont("monospace", 16)

    def draw_status(text):
        pygame.draw.rect(screen, BG_COLOR, pygame.Rect(0, win_h - 46, win_w, 46))
        screen.blit(font.render(text, True, BLACK), (MARGIN, win_h - 34))
        pygame.display.flip()

    def handle_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r:
                    main(); return

    #Generate
    maze = Maze(ROWS, COLS)
    # Entry gap on the LEFT edge (row 0)
    maze.eastWall[0][0] = 0
    # Exit gap on the RIGHT edge (top row)
    maze.eastWall[ROWS - 1][COLS] = 0
    # Open bottom wall for start cell
    maze.northWall[0][0] = 0
    # Open top wall for end cell 
    maze.northWall[ROWS][COLS - 1] = 0

    gen      = MazeGenerator(maze)
    renderer = Renderer(maze, screen)
    timer    = 0

    while not gen.done:
        handle_events()
        now = pygame.time.get_ticks()
        if now - timer >= GEN_DELAY:
            gen.step()
            timer = now
        renderer.draw_all(gen=gen)
        visited = sum(gen.visited[r][c] for r in range(ROWS) for c in range(COLS))
        draw_status(f"Generating...  {visited}/{ROWS * COLS} cells visited   [R] restart  [ESC] quit")
        clock.tick(60)

    renderer.draw_all(gen=gen)
    draw_status("Maze complete! Solving in 1 second...")
    pygame.time.wait(1000)

    #Solve
    start  = (0, 0)
    end    = (ROWS - 1, COLS - 1)
    solver = MazeSolver(maze, start, end)
    timer  = 0

    while not solver.done:
        handle_events()
        now = pygame.time.get_ticks()
        if now - timer >= SOLVE_DELAY:
            solver.step()
            timer = now
        renderer.draw_all(solver=solver)
        draw_status(f"Solving...  stack: {len(solver.stack)}  dead ends: {len(solver.dead_ends)}   [R] restart  [ESC] quit")
        clock.tick(60)

    #Show solution
    renderer.draw_all(solver=solver)
    draw_status(f"Solved!  Path length: {len(solver.solution)} cells.   [R] new maze  [ESC] quit")
    pygame.display.flip()

    while True:
        handle_events()
        clock.tick(30)

if __name__ == "__main__":
    main()