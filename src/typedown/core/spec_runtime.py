from typing import Any, Callable, Type
import functools

class TypedownSpecError(Exception):
    pass

def target(*, type: str = None, tags: list[str] = None):
    """
    Decorator to mark a function as a Spec test.
    
    Args:
        type: The entity type (ClassName) this test targets.
        tags: List of tags this test targets (not yet implemented in runner).
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Attach metadata to the wrapper function
        wrapper.__typedown_spec__ = {
            "type": type,
            "tags": tags or []
        }
        return wrapper
    return decorator
