import cv2
import os
from utils import is_exist, correct_degree_unicode, LAT, LOT
from coordinates import get_latlot, is_overlay
from logging_config import logging


def crop_image(img, save_path: str, src_point: tuple, dst_point: tuple) -> bool:
    """
    Crop the given image based on the source and destination coordinates.
    """
    try:
        src_h, src_w, _ = img.shape
        src_topleft, src_bottomright = src_point
        dst_topleft, dst_bottomright = dst_point

        # Calculate differences in latitude and longitude
        src_diff_lat = src_topleft[LAT] - src_bottomright[LAT]
        src_diff_lot = src_bottomright[LOT] - src_topleft[LOT]

        # Calculate the rectangle coordinate for the destination image
        delta_topleft_coord = (
            src_topleft[LAT] - dst_topleft[LAT],
            dst_topleft[LOT] - src_topleft[LOT],
        )
        delta_bottomright_coord = (
            src_topleft[LAT] - dst_bottomright[LAT],
            dst_bottomright[LOT] - src_topleft[LOT],
        )

        # Calculate pixel deltas for cropping
        delta_topleft_pixel_y = int(src_h * delta_topleft_coord[LAT] / src_diff_lat)
        delta_topleft_pixel_x = int(src_w * delta_topleft_coord[LOT] / src_diff_lot)
        delta_bottomright_pixel_y = int(
            src_h * delta_bottomright_coord[LAT] / src_diff_lat
        )
        delta_bottomright_pixel_x = int(
            src_w * delta_bottomright_coord[LOT] / src_diff_lot
        )

        # Perform cropping and save the image
        cropped = img[
            delta_topleft_pixel_y:delta_bottomright_pixel_y,
            delta_topleft_pixel_x:delta_bottomright_pixel_x,
        ]
        cv2.imwrite(save_path, cropped)
        return True
    except Exception as e:
        logging.error(f"Error cropping image {save_path}: {e}")
        return False


def preprocess_maps(map_file, map_path, output_path):
    """
    Preprocess maps by copying image to the output directory according to the pgw files.
    This function simulates the preprocessing step originally in run_first.py.
    """
    filename, extension = map_file.split(".")

    img = cv2.imread(os.path.join(map_path, filename + ".png"))
    y, x, _ = img.shape

    with open(os.path.join(map_path, map_file)) as pgw_file:
        trans = pgw_file.readlines()

    a, d, b, e, c, f = trans

    scale_lot, scale_lat = float(a), float(e)
    upper_lot, upper_lat = float(c), float(f)
    lower_lot, lower_lat = scale_lot * x + upper_lot, scale_lat * y + upper_lat

    new_name = (
        str(lower_lat)
        + "_"
        + str(upper_lot)
        + "__"
        + str(upper_lat)
        + "_"
        + str(lower_lot)
        + ".png"
    )

    cv2.imwrite(os.path.join(output_path, new_name), img)
    logging.info(f"Generated new map file {new_name} to output folder.")


def process_image_with_coords(img, img_path, out_path, final_coords):
    """
    Process an image by checking if it overlaps with any coordinates and cropping accordingly.
    """
    logging.info(f"Processing image: {img}")
    src_img = cv2.imread(os.path.join(img_path, img))
    src_point = get_latlot(img_name=img)

    for coord in final_coords:
        dst_point = get_latlot(coord_name=coord)
        img_name = coord[:-4] + ".jpg"
        save_path = os.path.join(out_path, img_name)

        if not is_exist(save_path) and is_overlay(src_point, dst_point):
            success = crop_image(src_img, save_path, src_point, dst_point)
            if success:
                command = f"ren {os.path.join(out_path, correct_degree_unicode(img_name))} {img_name}"
                os.system(command)
                logging.info(f"Successfully processed {img_name}")
