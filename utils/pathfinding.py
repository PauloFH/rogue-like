"""
Utilitários de Pathfinding (Busca de Caminho)

Este arquivo contém o algoritmo A* para encontrar o caminho mais curto entre
dois pontos em uma grade, evitando obstáculos.
"""
import heapq
import math

def heuristic(a, b):
    """
    Calcula a heurística de distância de Manhattan entre dois pontos.
    Usada pelo A* para estimar o custo restante até o objetivo.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, is_blocked, grid_width, grid_height):
    """
    Implementação do algoritmo de busca de caminho A*.

    Funciona em uma grade e retorna uma lista de tuplas de coordenadas
    representando o caminho do início ao fim.

    Args:
        start (tuple): A coordenada (x, y) de início na grade.
        goal (tuple): A coordenada (x, y) do objetivo na grade.
        is_blocked (function): Uma função que recebe (x, y) e retorna True se
                               a célula estiver bloqueada, False caso contrário.
        grid_width (int): A largura da grade.
        grid_height (int): A altura da grade.

    Returns:
        list: Uma lista de tuplas (x, y) representando o caminho, ou uma
              lista vazia se nenhum caminho for encontrado.
    """
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
        # Considera os 4 vizinhos (norte, sul, leste, oeste)
        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            # Verifica se o vizinho está dentro dos limites da grade
            if not (0 <= nx < grid_width and 0 <= ny < grid_height):
                continue
            
            # Verifica se o vizinho é um obstáculo
            if is_blocked(nx, ny):
                continue

            # Custo do caminho do início até o vizinho
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score.get((nx, ny), math.inf):
                # Este é o melhor caminho até agora para este vizinho. Registra!
                came_from[(nx, ny)] = current
                g_score[(nx, ny)] = tentative_g_score
                f_score = tentative_g_score + heuristic((nx, ny), goal)
                heapq.heappush(open_set, (f_score, (nx, ny)))

    return []  # Retorna lista vazia se não houver caminho