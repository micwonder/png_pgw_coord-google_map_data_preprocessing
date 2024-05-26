import os

LAT = 0
LOT = 1

map_path = "maps"
coord_path = "coordinates"
img_path = "output"
out_path = "fragments"

OLD_CHAR_DEGREE = "Â°"
CHAR_DEGREE = "°"


def is_exist(file_path: str) -> bool:
    """Check if a file exists at the given path."""
    return os.path.exists(file_path)


def correct_degree_unicode(filename: str) -> str:
    """Replace incorrect degree symbols in filenames."""
    return filename.replace(CHAR_DEGREE, OLD_CHAR_DEGREE)
