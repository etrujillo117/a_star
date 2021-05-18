#!/usr/bin/python
#Program to make an interactive grid for A* implementation

from threading import current_thread
import pygame
import math
from queue import PriorityQueue

WIDTH = 900
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Edgar's A* Pathfinder Algo")

#Colors used in display
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0,255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

#Class to represent part of the grid
class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x_len = row * width
        self.y_len = col * width
        self.color  = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    #Position of spot
    def get_pos(self):
        return self.row, self.col

    #Function that determines if spot is open
    def is_open(self):
        return self.color == GREEN
    
    def make_open(self):
        self.color = GREEN

    #Function that determines if spot will no longer be looked at
    def is_closed(self):
        return self.color == RED
    
    def make_closed(self):
        self.color = RED

    #Function that determines if spot is a barrier
    def is_barrier(self):
        return self.color == BLACK

    def make_barrier(self):
        self.color = BLACK

    #Function that determines if spot is start
    def is_start(self):
        return self.color == ORANGE

    def make_start(self):
        self.color = ORANGE
    
    #Function that determines if spot is finish
    def is_end(self):
        return self.color == BLUE

    def make_end(self):
        self.color = BLUE

    #Function thats highlights path
    def make_path(self):
        self.color = TURQUOISE

    #Function that resets spot
    def reset(self):
        self.color = WHITE

    #Function to draw the grid
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x_len, self.y_len, self.width, self.width))

    #Function to update neighbor spots
    def update_neighbors(self, grid):
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier(): #DOWN check
            self.neighbors.append(grid[self.row+1][self.col])

        if self.row > 0 and not grid[self.row-1][self.col].is_barrier(): #UP check
            self.neighbors.append(grid[self.row-1][self.col])

        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier(): #RIGHT check
            self.neighbors.append(grid[self.row][self.col+1])

        if self.row > 0 and not grid[self.row][self.col-1].is_barrier(): #LEFT check
            self.neighbors.append(grid[self.row][self.col-1])

    #Function to determine < or > between spots
    def __lt__(self, other):
        return False

#Function to calculate heuristic value in A* algorithm
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x2-x1) + abs(y2-y1)

#Function to reconstruct path
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

#A_Star Algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot : float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot : float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        
        draw()

        if current != start:
            current.make_closed()

    return False

#Function to make grid
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
            if i == 0 or j == 0 or i == rows-1 or j == rows-1:
                spot.make_barrier()

    return grid

#Function to draw gridlines
def draw_grid(win, rows, width):
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap),(width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))

#Function to excecute drawings and display
def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

#Helper function to translate mouse to grid
def get_clicked_pos(pos, rows, width):
    gap = width//rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

#Main function
def main(win, width):
    #Adaptable size
    ROWS = 50
    grid = make_grid(ROWS, width)

    #Game states
    start = None
    end = None
    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if pygame.mouse.get_pressed()[0]:  #Left click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]

                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()


            elif pygame.mouse.get_pressed()[2]:  #Right click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)