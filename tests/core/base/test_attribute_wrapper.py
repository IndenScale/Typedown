
import yaml
from typedown.core.base.utils import AttributeWrapper

def test_attribute_wrapper_yaml_types():
    """
    Scenario from legacy reproduce_issue.py: Verify AttributeWrapper 
    handles YAML native types (like date) correctly.
    """
    code = """
title: "History Book"
published_date: 1990-01-01
"""
    data = yaml.safe_load(code)
    
    # Ensure YAML parser loaded it as a date object (or similar)
    # depending on yaml version, but safe_load usually results in date for this format
    wrapper = AttributeWrapper(data, entity_id="book1")
    
    assert wrapper.title == "History Book"
    assert wrapper.published_date == data.get('published_date')
    
    # Test a date in the far future (which was the specific case in reproduce_issue.py)
    code_future = "published_date: 2099-01-01"
    data_future = yaml.safe_load(code_future)
    wrapper_future = AttributeWrapper(data_future, entity_id="book2")
    
    assert wrapper_future.published_date == data_future.get('published_date')
