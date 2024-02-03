import copy

# def generate_maze(rows, cols, start, end, density=0.2):
#     maze = [[0] * cols for _ in range(rows)]
#     for i in range(rows):
#         for j in range(cols):
#             if i == start[0] and j == start[1]:
#                 maze[i][j] = 0  # Start point
#             elif i == end[0] and j == end[1]:
#                 maze[i][j] = 0  # End point
#             elif random() < density:
#                 maze[i][j] = 1  # Wall
#             else:
#                 maze[i][j] = 0  # Open path
#     return maze
#
# def heuristic(a, b):
#     return abs(a[0] - b[0]) + abs(a[1] - b[1])
#
# def get_direction(prev_pos, current_pos):
#     if current_pos[0] < prev_pos[0]:
#         return 0  # Up
#     elif current_pos[0] > prev_pos[0]:
#         return 1  # Down
#     elif current_pos[1] < prev_pos[1]:
#         return 2  # Left
#     elif current_pos[1] > prev_pos[1]:
#         return 3  # Right

def astar(maze, start :tuple, end):
    m = [[0] * 16 for i in range(16)]
    m[start[1]][start[0]] = 1
    a = copy.copy(maze)
    end = end[::-1]
    def make_step(k):
        for i in range(len(m)):
            for j in range(len(m[i])):
                if m[i][j] == k:
                    if i > 0 and m[i - 1][j] == 0 and a[i - 1][j] == 0:
                        m[i - 1][j] = k + 1
                    if j > 0 and m[i][j - 1] == 0 and a[i][j - 1] == 0:
                        m[i][j - 1] = k + 1
                    if i < len(m) - 1 and m[i + 1][j] == 0 and a[i + 1][j] == 0:
                        m[i + 1][j] = k + 1
                    if j < len(m[i]) - 1 and m[i][j + 1] == 0 and a[i][j + 1] == 0:
                        m[i][j + 1] = k + 1

    k = 0
    while m[end[0]][end[1]] == 0:
        k += 1
        make_step(k)
    i, j = end
    k = m[i][j]
    the_path = [(i, j)]
    while k > 1:
        if i > 0 and m[i - 1][j] == k - 1:
            i, j = i - 1, j
            the_path.append((i, j))
            k -= 1
        elif j > 0 and m[i][j - 1] == k - 1:
            i, j = i, j - 1
            the_path.append((i, j))
            k -= 1
        elif i < len(m) - 1 and m[i + 1][j] == k - 1:
            i, j = i + 1, j
            the_path.append((i, j))
            k -= 1
        elif j < len(m[i]) - 1 and m[i][j + 1] == k - 1:
            i, j = i, j + 1
            the_path.append((i, j))
            k -= 1
    return the_path[::-1]