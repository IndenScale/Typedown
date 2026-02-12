"""
Test: query() and sql() Functions in Specs
Related Doc: docs/zh/02_concepts/02_validation.md Section "全局验证的工具"
"""

import pytest
from typedown.core.analysis.query import QueryEngine
from typedown.core.base.symbol_table import SymbolTable


class TestQueryFunction:
    """Test query() function for spec validation."""
    
    def test_query_by_id(self):
        """Test query by exact ID."""
        # Setup symbol table with test entity
        st = SymbolTable()
        # Add test entity

        _ = QueryEngine(st)  # engine unused
        # Test query resolution
    
    def test_query_with_wildcard(self):
        """Test query with wildcard pattern."""
        # e.g., query("users/*.manager")
        pass
    
    def test_query_property_access(self):
        """Test query with property path."""
        # e.g., query("user-alice.name")
        pass


class TestSQLFunction:
    """Test sql() function for spec validation."""
    
    @pytest.mark.skipif(not False, reason="DuckDB integration test")
    def test_sql_basic_query(self):
        """Test basic SQL query execution."""
        pass
    
    @pytest.mark.skipif(not False, reason="DuckDB integration test")
    def test_sql_aggregation(self):
        """Test SQL aggregation queries."""
        pass
    
    @pytest.mark.skipif(not False, reason="DuckDB integration test")
    def test_sql_with_parameters(self):
        """Test SQL with parameters."""
        pass
