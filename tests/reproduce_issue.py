
import yaml
import datetime
from typedown.core.base.utils import AttributeWrapper
from typedown.core.ast import EntityBlock

def reproduce():
    # 1. Simulate Parsing
    code_old = """
title: "Generic History Book"
published_date: 1990-01-01
"""
    code_future = """
title: "Time Traveler's Guide"
published_date: 2099-01-01
"""

    data_old = yaml.safe_load(code_old)
    data_future = yaml.safe_load(code_future)

    print(f"Old Book Data: {data_old}")
    print(f"Old Book published_date type: {type(data_old.get('published_date'))}")
    
    print(f"Future Book Data: {data_future}")
    print(f"Future Book published_date type: {type(data_future.get('published_date'))}")

    # 2. Simulate AttributeWrapper
    wrapper_old = AttributeWrapper(data_old, entity_id="old_book")
    wrapper_future = AttributeWrapper(data_future, entity_id="future_book")

    # 3. Simulate Spec Logic
    try:
        print(f"Old Book published_date via wrapper: {wrapper_old.published_date}")
    except AttributeError as e:
        print(f"ERROR accessing old_book.published_date: {e}")

    try:
        print(f"Future Book published_date via wrapper: {wrapper_future.published_date}")
    except AttributeError as e:
        print(f"ERROR accessing future_book.published_date: {e}")

if __name__ == "__main__":
    reproduce()
