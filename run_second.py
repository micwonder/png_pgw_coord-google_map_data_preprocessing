import os
import cv2
import time
import glob
import argparse

LAT = 0
LOT = 1

OLD_CHAR_DEGREE = "Â°"
CHAR_DEGREE = "°"


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


def main_one_process():

    out_path = "fragments"
    img_path = "output"
    coord_path = "coordinates"

    os.makedirs(out_path, exist_ok=True)

    # files = glob.glob(f'{coord_path}/*/*.txt')
    # len_files = len(files)
    len_files = 777600

    final_status = []
    final_coords = []

    count = 0
    for coord_file in os.listdir(coord_path):
        sub_dir = os.path.join(coord_path, coord_file)
        if os.path.isdir(sub_dir):
            final_coords += os.listdir(sub_dir)

    print(len(final_coords))
    is_success = False

    for img in os.listdir(img_path):
        print(img)
        src_img = cv2.imread(os.path.join(img_path, img))

        src_point = get_latlot(img_name=img)

        for coord in final_coords:
            count = count + 1
            dst_point = get_latlot(coord_name=coord)

            img_name = coord[:-4] + ".jpg"
            save_path = os.path.join(out_path, img_name)

            if is_exist(save_path):
                is_success = True

            if is_overlay(src_point, dst_point):
                is_success = crop_image(src_img, save_path, src_point, dst_point)
                if is_success:
                    command = f"ren { os.path.join(out_path, correct_degree_unicode(img_name)) } { img_name }"
                    os.system(command)

                    logger = f">>>>>>>>>>>>>>>>>>>> { count } -------------> { is_success } \n"
                    final_status.append(logger)
                    final_status.append(f"{ sub_dir } \\ { img }")
                    final_status.append("\n\n\n")
                    print(logger)

                    with open("final_status.txt", "w", encoding="utf-8") as file:
                        file.writelines(final_status)

    print(count)


if __name__ == "__main__":
    main_one_process()

# def run():
#     out_path = "fragments_new"
#     img_path = "output"
#     coord_path = "coordinates"

#     os.makedirs(out_path, exist_ok=True)

#     coord_info = []
#     for coord_file in os.listdir(coord_path):
#         for sub_dir in [os.path.join(coord_path, coord_file)]:
#             if os.path.isdir(sub_dir):
#                 for filename in os.listdir(sub_dir):
#                     img_name = filename[:-4] + ".jpg"
#                     save_path = os.path.join(out_path, img_name)
#                     if is_exist(save_path):
#                         coord_info.append((filename, img_name, save_path))

#     print(len(coord_info))

#     map_img_info = [(img, os.path.join(img_path, img)) for img in os.listdir(img_path)]

#     print(len(map_img_info))

#     # process_coordinate_file(coord_info, map_img_info)

#     # with ProcessPoolExecutor(max_workers=len(map_img_info)) as executor:
#     #     process_partial = partial()

#     # process_coordinate_file()


# if __name__ == "__main__":
#     run()
