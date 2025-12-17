import sys
import typedown
import typedown.core.workspace
import typedown.core.loader

print(f"Python Executable: {sys.executable}")
print(f"Typedown Package: {typedown.__file__}")
print(f"Workspace Module: {typedown.core.workspace.__file__}")
print(f"Loader Module: {typedown.core.loader.__file__}")
