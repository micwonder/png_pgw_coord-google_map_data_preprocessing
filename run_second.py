from concurrent.futures import ProcessPoolExecutor
from functools import partial
import logging
import os
import cv2
import time
import glob
import argparse

from tqdm import tqdm

LAT = 0
LOT = 1

OLD_CHAR_DEGREE = "Â°"
CHAR_DEGREE = "°"

# Set up logging
logging.basicConfig(
    filename="process.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def crop_image(img, save_path: str, src_point: tuple, dst_point: tuple):

    src_h, src_w, _ = img.shape

    src_topleft, src_bottomright = src_point
    dst_topleft, dst_bottomright = dst_point

    src_diff_lat, src_diff_lot = (
        src_topleft[LAT] - src_bottomright[LAT],
        src_bottomright[LOT] - src_topleft[LOT],
    )
    dst_diff_lat, dst_diff_lot = (
        dst_topleft[LAT] - dst_bottomright[LAT],
        dst_bottomright[LOT] - dst_topleft[LOT],
    )

    dst_h, dst_w = int(src_h * dst_diff_lat / src_diff_lat), int(
        src_w * dst_diff_lot / src_diff_lot
    )

    delta_topleft_coord = (
        src_topleft[LAT] - dst_topleft[LAT],
        dst_topleft[LOT] - src_topleft[LOT],
    )
    delta_bottomright_coord = (
        src_topleft[LAT] - dst_bottomright[LAT],
        dst_bottomright[LOT] - src_topleft[LOT],
    )

    delta_topleft_pixel_y, delta_topleft_pixel_x = int(
        src_h * delta_topleft_coord[LAT] / src_diff_lat
    ), int(src_w * delta_topleft_coord[LOT] / src_diff_lot)
    delta_bottomright_pixel_y, delta_bottomright_pixel_x = int(
        src_h * delta_bottomright_coord[LAT] / src_diff_lat
    ), int(src_w * delta_bottomright_coord[LOT] / src_diff_lot)

    try:
        cropped = img[
            delta_topleft_pixel_y:delta_bottomright_pixel_y,
            delta_topleft_pixel_x:delta_bottomright_pixel_x,
        ]
        cv2.imwrite(save_path, cropped)
        return True
    except Exception as e:
        print(e)
        return False


def is_overlay(src_point: tuple, dst_point: tuple):

    src_topleft, src_bottomright = src_point
    dst_topleft, dst_bottomright = dst_point
    if (
        src_topleft[LAT] > dst_topleft[LAT]
        and src_topleft[LOT] < dst_topleft[LOT]
        and src_bottomright[LAT] < dst_bottomright[LAT]
        and src_bottomright[LOT] > dst_bottomright[LOT]
    ):
        return True
    else:
        return False


def dms_to_float(dms: str):
    degree = dms.split("°")[0]
    minute = dms.split("°")[1].split("'")[0]
    second = dms.split("°")[1].split("'")[1][:-1]

    return float(degree) + float(minute) / 60 + float(second) / 3600


def get_latlot(img_name: str = None, coord_name: str = None):

    #
    # sample img_name
    # 38.158316657442_127.59521484375__38.3201108450154_127.68310546875.png
    #
    if img_name is not None:
        lower_lat, upper_lot, _, upper_lat, lower_lot = img_name[:-4].split("_")
        lower_lat, upper_lot, upper_lat, lower_lot = (
            float(lower_lat),
            float(upper_lot),
            float(upper_lat),
            float(lower_lot),
        )
        return ((upper_lat, upper_lot), (lower_lat, lower_lot))

    #
    # sample coord_name
    # 37°0'19.500000000007844N_126°0'20.49999999999841E_36°59'59.50000000001751N_126°0'40.500000000014325E.txt
    #
    elif coord_name is not None:
        upper_lat, upper_lot, lower_lat, lower_lot = coord_name[:-4].split("_")
        upper_lat = dms_to_float(upper_lat)
        upper_lot = dms_to_float(upper_lot)
        lower_lat = dms_to_float(lower_lat)
        lower_lot = dms_to_float(lower_lot)
        return ((upper_lat, upper_lot), (lower_lat, lower_lot))

    else:
        return "Anyone must be None"


def is_exist(coor_file: str):
    if os.path.exists(coor_file):
        return True
    else:
        return False


def correct_degree_unicode(filename: str):
    filename = filename.replace(CHAR_DEGREE, OLD_CHAR_DEGREE)
    return filename


def process_image_with_coords(img, img_path, out_path, final_coords):
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
                command = f"ren { os.path.join(out_path, correct_degree_unicode(img_name)) } { img_name }"
                os.system(command)
                logging.info(f"Successfully processed {img_name}")


def main_one_process():
    out_path = "fragments"
    img_path = "output"
    coord_path = "coordinates"

    os.makedirs(out_path, exist_ok=True)

    final_coords = [file for _, _, files in os.walk(coord_path) for file in files]

    img_files = os.listdir(img_path)
    logging.info(f"Total images: {len(img_files)}")
    logging.info(f"Total coordinates: {len(final_coords)}")

    with ProcessPoolExecutor(max_workers=len(img_files)) as executor:
        process_partial = partial(
            process_image_with_coords,
            img_path=img_path,
            out_path=out_path,
            final_coords=final_coords,
        )
        list(tqdm(executor.map(process_partial, img_files), total=len(img_files)))


if __name__ == "__main__":
    main_one_process()
