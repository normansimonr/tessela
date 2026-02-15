import os
import csv
from PIL import Image
import pytesseract

def ocr_images_in_directory(directory_path, output_csv_path):
    """
    Performs OCR on all images in a directory and its subdirectories,
    saving the results to a CSV file.

    Args:
        directory_path (str): The path to the directory containing the images.
        output_csv_path (str): The path to the output CSV file.
    """
    results = []
    for volume_folder in sorted(os.listdir(directory_path)):
        volume_path = os.path.join(directory_path, volume_folder)
        if os.path.isdir(volume_path):
            for image_file in sorted(os.listdir(volume_path)):
                if image_file.endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(volume_path, image_file)
                    try:
                        text = pytesseract.image_to_string(Image.open(image_path)).strip()
                        results.append({
                            'volume': volume_folder,
                            'page': image_file,
                            'text': text
                        })
                        print(f"Processed {image_path}")
                    except Exception as e:
                        print(f"Error processing {image_path}: {e}")

    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['volume', 'page', 'text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nOCR results saved to {output_csv_path}")

if __name__ == "__main__":
    HEADERS_DIR = 'headers'
    OUTPUT_CSV = 'ocr_results.csv'
    ocr_images_in_directory(HEADERS_DIR, OUTPUT_CSV)
