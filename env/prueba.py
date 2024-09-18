import importlib

try:
    importlib.import_module('pydot')
    print("pydot importado correctamente")
except ImportError as e:
    print(f"Error al importar pydot: {e}")