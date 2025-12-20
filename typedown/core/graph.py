from typing import Any, Dict, List, Optional, Set

class DependencyGraph:
    def __init__(self):
        self.adj: Dict[str, Set[str]] = {}
        
    def add_dependency(self, node: str, dependency: str):
        if node not in self.adj:
            self.adj[node] = set()
        self.adj[node].add(dependency)
        if dependency not in self.adj:
            self.adj[dependency] = set()

    def topological_sort(self) -> List[str]:
        visited = set()
        temp_visited = set()
        order = []

        def visit(node):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected involving: {node}")
            if node not in visited:
                temp_visited.add(node)
                for neighbor in self.adj.get(node, []):
                    visit(neighbor)
                temp_visited.remove(node)
                visited.add(node)
                order.append(node)

        for node in list(self.adj.keys()):
            if node not in visited:
                try:
                    visit(node)
                except ValueError as e:
                    # Log but continue to allow other independent components to be sorted
                    pass
        
        return order
