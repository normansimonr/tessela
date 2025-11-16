
import os
import csv
from PIL import Image

def get_crop_coordinates(csv_path):
    """Reads cropping coordinates from a CSV file for each volume."""
    coordinates = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            volume = row['volume']
            coordinates[volume] = {
                'even': {
                    'x1': int(row['x0even']),
                    'y1': int(row['y0']),
                    'x2': int(row['x1even']),
                    'y2': int(row['y1']),
                },
                'odd': {
                    'x1': int(row['x0odd']),
                    'y1': int(row['y0']),
                    'x2': int(row['x1odd']),
                    'y2': int(row['y1']),
                }
            }
    return coordinates

def process_images(images_dir, headers_dir, coordinates):
    """
    Crops images based on volume-specific coordinates and saves them.
    """
    if not os.path.exists(headers_dir):
        os.makedirs(headers_dir)

    for volume in os.listdir(images_dir):
        volume_path = os.path.join(images_dir, volume)
        if not os.path.isdir(volume_path):
            continue

        if volume not in coordinates:
            print(f"Warning: No coordinates found for volume '{volume}'. Skipping this volume.")
            continue
        
        volume_coords = coordinates[volume]

        output_volume_path = os.path.join(headers_dir, volume)
        if os.path.exists(output_volume_path):
            print(f"Skipping volume {volume} as output directory already exists.")
            continue
        os.makedirs(output_volume_path)

        for image_name in os.listdir(volume_path):
            if not image_name.lower().endswith('.png'):
                continue

            image_path = os.path.join(volume_path, image_name)
            try:
                page_number = int(os.path.splitext(image_name)[0])
            except ValueError:
                print(f"Warning: Could not determine page number from filename '{image_name}'. Skipping.")
                continue

            page_type = 'odd' if page_number % 2 != 0 else 'even'
            
            coords_for_page = volume_coords[page_type]

            try:
                with Image.open(image_path) as img:
                    crop_box = (
                        coords_for_page['x1'],
                        coords_for_page['y1'],
                        coords_for_page['x2'],
                        coords_for_page['y2'],
                    )
                    header = img.crop(crop_box)
                    output_path = os.path.join(output_volume_path, image_name)
                    header.save(output_path)
                    print(f"Saved header for {image_path} to {output_path}")
            except Exception as e:
                print(f"Error processing {image_path}: {e}")


if __name__ == "__main__":
    IMAGES_DIR = 'images'
    HEADERS_DIR = 'headers'
    COORDINATES_CSV = 'header_coordinates.csv'

    try:
        crop_coordinates = get_crop_coordinates(COORDINATES_CSV)
        process_images(IMAGES_DIR, HEADERS_DIR, crop_coordinates)
        print("\nProcessing complete.")
    except FileNotFoundError:
        print(f"Error: The file {COORDINATES_CSV} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
