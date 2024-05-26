# Image Cropping Project

This project processes images based on provided coordinates, crops them accordingly, and saves the results. Follow the steps below to set up and run the project.

## Project Structure

```markdown
project/
│
├── main.py
├── utils.py
├── image_processing.py
├── coordinates.py
├── logging_config.py
├── run_first.py (Deprecated, functionality moved to main.py)
├── run_second.py (Beta)
├── maps/
├── coordinates/
├── fragments/
└── output/
```

## Prerequisites

- Python 3.x
- Required Python packages (listed in `requirements.txt`)

## Setup

1. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2. **Create necessary directories** (if they do not exist):

    ```bash
    mkdir maps coordinates fragments output
    ```

## Instructions

1. **Copy downloaded images into the 'maps' folder**:

    Place all your image files that need to be processed in the `maps` folder.

2. **Copy received coordinates text files into the 'coordinates' folder**:

    Place all your coordinate text files in the `coordinates` folder.

3. **Run 'python main.py'**:

    This script will preprocess the images and then process them based on the coordinates.

    ```bash
    python main.py
    ```

4. **Run 'python run_second.py' (Beta)**:

    This script is an alternative approach for processing images and coordinates.

    ```bash
    python run_second.py
    ```

5. **Archive 'fragments' and 'output' folder**:

    After processing, archive the `fragments` and `output` folders as required.

    ```bash
    tar -czf fragments.tar.gz fragments
    tar -czf output.tar.gz output
    ```

## File Descriptions

- **main.py**: The main entry point for the project, including preprocessing and image processing.
- **utils.py**: Contains utility functions for file operations and string manipulations.
- **image_processing.py**: Handles the image processing and cropping functions.
- **coordinates.py**: Manages coordinate-related functions.
- **maps/**: Directory where downloaded images should be placed.
- **coordinates/**: Directory where received coordinate text files should be placed.
- **fragments/**: Directory where cropped image fragments will be saved.
- **output/**: Directory for other output files.
- **logging_config.py**: Sets up logging configuration.
- **run_first.py**: Deprecated, preprocessing functionality moved to `main.py`.
- **run_second.py**: Deprecated, Beta version of the image processing script.

## Logging

Logs are saved in `process.log` for detailed tracking of the processing steps and any errors that occur.

## Notes

- Ensure that the `maps` and `coordinates` folders are populated with the necessary files before running the scripts.
- The `main.py` script uses parallel processing to speed up the image processing. Adjust the `max_workers` parameter in the script if necessary based on your system's capabilities.
