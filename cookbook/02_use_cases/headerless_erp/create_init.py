# create __init__.py files
import os

files = [
    "/Users/indenscale/Documents/Projects/Typedown/use_cases/headerless_erp/models/__init__.py",
    "/Users/indenscale/Documents/Projects/Typedown/use_cases/headerless_erp/models/core/__init__.py",
    "/Users/indenscale/Documents/Projects/Typedown/use_cases/headerless_erp/models/org/__init__.py",
    "/Users/indenscale/Documents/Projects/Typedown/use_cases/headerless_erp/models/pmo/__init__.py",
    "/Users/indenscale/Documents/Projects/Typedown/use_cases/headerless_erp/models/finance/__init__.py",
]

for f in files:
    with open(f, "w") as file:
        pass
