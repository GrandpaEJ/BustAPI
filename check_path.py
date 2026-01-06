import os
import sys

import bustapi

print(f"BustAPI Location: {bustapi.__file__}")
print(f"BustAPI Dir: {os.path.dirname(bustapi.__file__)}")
try:
    import bustapi.bustapi as core

    print(f"Core via bustapi.bustapi: {core}")
except ImportError:
    print("Could not import bustapi.bustapi")

try:
    import bustapi_core

    print(f"Core via bustapi_core: {bustapi_core}")
except ImportError:
    print("Could not import bustapi_core")

print(f"Sys Path: {sys.path}")
