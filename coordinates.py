import os
from utils import LAT, LOT


def get_latlot(img_name: str = None, coord_name: str = None):
    """
    Extract latitude and longitude from image or coordinate filenames.
    """
    if img_name:
        # Split img_name and filter out empty strings
        parts = [part for part in img_name[:-4].split("_") if part]
        # Convert the non-empty parts to float
        lower_lat, upper_lot, upper_lat, lower_lot = map(float, parts)

        return (upper_lat, upper_lot), (lower_lat, lower_lot)
    elif coord_name:
        # Split coord_name and filter out empty strings
        parts = [part for part in coord_name[:-4].split("_")]
        # Convert the non-empty parts to float
        upper_lat, upper_lot, lower_lat, lower_lot = map(dms_to_float, parts)
        print(upper_lat)
        return (upper_lat, upper_lot), (lower_lat, lower_lot)
    else:
        return None


def is_overlay(src_point: tuple, dst_point: tuple) -> bool:
    """
    Check if the destination coordinates are within the source coordinates.
    """
    src_topleft, src_bottomright = src_point
    dst_topleft, dst_bottomright = dst_point
    return (
        src_topleft[LAT] > dst_topleft[LAT]
        and src_topleft[LOT] < dst_topleft[LOT]
        and src_bottomright[LAT] < dst_bottomright[LAT]
        and src_bottomright[LOT] > dst_bottomright[LOT]
    )


def dms_to_float(dms: str) -> float:
    """
    Convert DMS (Degrees, Minutes, Seconds) format to float.
    """
    degree, minute, second = (
        dms.split("°")[0],
        dms.split("°")[1].split("'")[0],
        dms.split("°")[1].split("'")[1][:-1],
    )
    return float(degree) + float(minute) / 60 + float(second) / 3600


def get_all_coords(coord_path: str) -> list:
    """
    Get all coordinate filenames from the given directory.
    """
    return [file for _, _, files in os.walk(coord_path) for file in files]
