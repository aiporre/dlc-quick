from gui.utils.parse_yaml import parse_yaml
from gui.utils.interpolation import uniform_interpolation
import gui.static as static
def _get_module_path(module):
    import os
    return os.path.abspath(module.__file__)
STATIC = _get_module_path(static)