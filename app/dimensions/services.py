from app.extensions import db
from .models import HierarchyEdge

class DimensionError(Exception):
    pass

# Detección de ciclos DFS en una jerarquía
# Retorna True si hay ciclo

def has_cycle(hierarchy_id: int) -> bool:
    from collections import defaultdict

    children = defaultdict(list)
    for e in HierarchyEdge.query.filter_by(hierarchy_id=hierarchy_id).all():
        if e.parent_member_id is not None:
            children[e.parent_member_id].append(e.child_member_id)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {}

    def dfs(u):
        color[u] = GRAY
        for v in children.get(u, []):
            if color.get(v, WHITE) == GRAY:
                return True
            if color.get(v, WHITE) == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    # Nodos raíz posibles: padres que no son hijos de nadie
    all_parents = set(children.keys())
    all_children = {c for lst in children.values() for c in lst}
    roots = list(all_parents - all_children)

    # También verificar componentes sueltos
    nodes = set(all_parents) | all_children

    for n in (roots or list(nodes)):
        if color.get(n, WHITE) == WHITE and dfs(n):
            return True
    return False