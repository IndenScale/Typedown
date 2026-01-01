from typing import Any, Dict, List, Optional, Set
from typedown.core.base.errors import CycleError

class DependencyGraph:
    def __init__(self):
        self.adj: Dict[str, Set[str]] = {}
        self.reverse_adj: Dict[str, Set[str]] = {}
        
    def add_dependency(self, node: str, dependency: str):
        if node not in self.adj:
            self.adj[node] = set()
        self.adj[node].add(dependency)
        
        # Maintain reverse graph: dependency is used by node
        if dependency not in self.reverse_adj:
            self.reverse_adj[dependency] = set()
        self.reverse_adj[dependency].add(node)

        # Ensure dependency exists in graph structure too
        if dependency not in self.adj:
            self.adj[dependency] = set()

    def topological_sort(self) -> List[str]:
        """
        Returns a list of nodes in topological order (dependencies first).
        Raises CycleError if a cycle is detected.
        """
        visited = set()
        temp_visited = set()
        order = []
        path_stack = [] # For nice error reporting

        def visit(node):
            if node in temp_visited:
                # Cycle detected!
                # Reconstruct path for error message
                cycle_path = " -> ".join(path_stack + [node])
                raise CycleError(f"Circular dependency detected: {cycle_path}")
            
            if node not in visited:
                temp_visited.add(node)
                path_stack.append(node)
                
                # Visit neighbors (dependencies)
                # Sort for deterministic output
                for neighbor in sorted(self.adj.get(node, [])):
                    visit(neighbor)
                
                path_stack.pop()
                temp_visited.remove(node)
                visited.add(node)
                order.append(node)

        # Visit all nodes
        # Sort keys for deterministic behavior
        for node in sorted(list(self.adj.keys())):
            if node not in visited:
                visit(node)
        
        return order
