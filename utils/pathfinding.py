import heapq, math
from settings import AREA_WIDTH, AREA_HEIGHT


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, is_blocked):
    open_set = [(0, start)]
    g_score = {start: 0}
    came_from = {}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        cx, cy = current
        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            if nx < 0 or ny < 0 or nx >= AREA_WIDTH or ny >= AREA_HEIGHT:
                continue
            if is_blocked(nx, ny):
                continue

            tentative = g_score[current] + 1
            if tentative < g_score.get((nx, ny), math.inf):
                came_from[(nx, ny)] = current
                g_score[(nx, ny)] = tentative
                f_score = tentative + heuristic((nx, ny), goal)
                heapq.heappush(open_set, (f_score, (nx, ny)))
    return []
