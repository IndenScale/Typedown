import pytest
from typedown.core.analysis.graph import DependencyGraph
from typedown.core.base.errors import CycleError

def test_topological_sort():
    dg = DependencyGraph()
    # A depends on B
    dg.add_dependency("A", "B")
    # B depends on C
    dg.add_dependency("B", "C")
    
    order = dg.topological_sort()
    # Dependencies first: C, B, A
    assert order == ["C", "B", "A"]

def test_independent_nodes():
    dg = DependencyGraph()
    dg.add_dependency("A", "B")
    dg.add_dependency("C", "D")
    order = dg.topological_sort()
    # Sorted alphabetically if independent: B, A, D, C
    # Wait, B and D are leaf dependencies.
    # Sorted order for visit is A, C. 
    # visit(A) -> visit(B) -> order=[B, A]
    # visit(C) -> visit(D) -> order=[B, A, D, C]
    assert order == ["B", "A", "D", "C"]

def test_cycle_detection():
    dg = DependencyGraph()
    dg.add_dependency("A", "B")
    dg.add_dependency("B", "C")
    dg.add_dependency("C", "A")
    
    with pytest.raises(CycleError) as excinfo:
        dg.topological_sort()
    assert "Circular dependency detected" in str(excinfo.value)
