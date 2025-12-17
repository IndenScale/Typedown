from typing import Dict, List, Set, Tuple
from collections import deque
from typedown.core.ast import EntityBlock, Project

class CircularDependencyError(Exception):
    pass

class Resolver:
    def __init__(self, project: Project):
        self.project = project
        self.dependency_graph: Dict[str, List[str]] = {} # id -> list of parent ids

    def build_graph(self):
        """
        Build the dependency graph from the symbol table.
        Dependencies include:
        1. Inheritance (former / derived_from)
        2. Content References ([[Target.attr]])
        """
        # Pre-calculate reference map: entity_id -> set(dependency_ids)
        ref_deps: Dict[str, Set[str]] = {}
        
        # We need to map References to Entities based on SourceLocation
        # Iterate over documents to do this mapping contextually
        for doc in self.project.documents.values():
            # For each document, check which references fall into which entity block
            
            # Optimization: Sort entities by start line (should be already ?)
            # Naive approach: for each ref, find the containing entity
            for ref in doc.references:
                ref_line = ref.location.line_start
                target_id = ref.query_string.split('.')[0] # "User.name" -> "User"
                
                # Check if this target exists in symbol table
                if target_id not in self.project.symbol_table:
                    # Ignore external/invalid refs here, Evaluator will catch them.
                    # Or should we enforce existence? 
                    # If we enforce, we might break on self-references inside the same block?
                    # Let's verify existence.
                    continue
                
                # Find the owner entity
                owner_entity = None
                for entity in doc.entities:
                    if entity.location.line_start <= ref_line <= entity.location.line_end:
                        owner_entity = entity
                        break
                
                if owner_entity:
                    if owner_entity.id not in ref_deps:
                        ref_deps[owner_entity.id] = set()
                    
                    # Avoid self-dependency (not circular, just no-op)
                    if target_id != owner_entity.id:
                        ref_deps[owner_entity.id].add(target_id)

        # Now build the full graph
        for entity_id, entity in self.project.symbol_table.items():
            deps = set()
            
            # 1. Structural Dependencies (Inheritance)
            if entity.former_ref:
                t = entity.former_ref.target_query
                if t in self.project.symbol_table: deps.add(t)
            
            if entity.derived_from_ref:
                t = entity.derived_from_ref.target_query
                if t in self.project.symbol_table: deps.add(t)
            
            # 2. Content Dependencies (References)
            if entity_id in ref_deps:
                deps.update(ref_deps[entity_id])
                
            self.project.dependency_graph[entity_id] = list(deps)

    def topological_sort(self) -> List[str]:
        """
        Return a list of entity IDs in instantiation order (Parents first).
        Uses Kahn's algorithm.
        """
        graph = self.project.dependency_graph
        
        # Rebuild graph as Adjacency List: Dependency -> [Dependents]
        # graph[u] = [deps] means u depends on deps.
        # Edge direction V -> U means V must complete before U starts.
        adj = {u: [] for u in graph}
        in_degree = {u: 0 for u in graph} 
        
        for u, deps in graph.items():
            for v in deps:
                # u depends on v. So v -> u edge.
                adj[v].append(u)
                in_degree[u] += 1
        
        # Queue of nodes with no dependencies
        queue = deque([u for u in in_degree if in_degree[u] == 0])
        sorted_list = []
        
        while queue:
            u = queue.popleft()
            sorted_list.append(u)
            
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        if len(sorted_list) != len(graph):
            # Debugging cycle
            remaining = [u for u in in_degree if in_degree[u] > 0]
            raise CircularDependencyError(f"Cycle detected involving entities: {remaining}")
            
        return sorted_list
