from concurrent.futures import ProcessPoolExecutor
from functools import partial
import os
from tqdm import tqdm
from logging_config import setup_logging, logging
from image_processing import preprocess_maps, process_image_with_coords
from coordinates import get_all_coords
from utils import map_path, img_path, out_path, coord_path


def main():
    """
    Main function to run the preprocessing and image processing steps.
    """
    setup_logging()

    # Determine the number of workers based on CPU count
    num_workers = os.cpu_count()
    logging.info(f"Using {num_workers} workers")

    # Ensure output directories exist
    for directory in [img_path, out_path]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    if not len(os.listdir(img_path)):
        # ? Step 1: Preprocess maps and save them to the output folder
        logging.info("Starting preprocessing of maps...")

        # List all map files
        map_files = [
            map_file
            for map_file in os.listdir(map_path)
            if map_file.split(".")[1] == "pgw"
        ]

        # Use ProcessPoolExecutor for parallel processing of images
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            process_partial = partial(
                preprocess_maps,
                map_path=map_path,
                output_path=img_path,
            )
            list(
                tqdm(
                    executor.map(process_partial, map_files),
                    total=len(map_files),
                    desc="Preprocessing",
                )
            )
        logging.info("Preprocessing complete.")

    # ? Step 2: Image processing with coordinates (Beta)

    os.makedirs(out_path, exist_ok=True)

    # Gather all coordinate files
    final_coords = get_all_coords(coord_path)

    # List all image files
    img_files = os.listdir(img_path)
    logging.info(f"Total images: {len(img_files)}")
    logging.info(f"Total coordinates: {len(final_coords)}")

    # Use ProcessPoolExecutor for parallel processing of images
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        process_partial = partial(
            process_image_with_coords,
            img_path=img_path,
            out_path=out_path,
            final_coords=final_coords,
        )
        list(
            tqdm(
                executor.map(process_partial, img_files),
                total=len(img_files),
                desc="Generating fragments",
            )
        )


if __name__ == "__main__":
    main()
