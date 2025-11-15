
import os
import pandas as pd
import requests
import fitz  # PyMuPDF

def download_and_convert_pdfs(csv_file):
    """
    Downloads PDFs from a CSV file, saves them, and converts each page to an image.
    It skips volumes that have already been processed.
    """
    # Create base directories if they don't exist
    pdfs_dir = 'pdfs'
    images_dir = 'images'
    os.makedirs(pdfs_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    # Read the CSV file
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        return

    # Process each row in the CSV
    for index, row in df.iterrows():
        try:
            volume = str(row['volume'])
            url = str(row['url'])
        except KeyError as e:
            print(f"Skipping row {index+2}: Missing expected column {e}.")
            continue

        pdf_path = os.path.join(pdfs_dir, f'{volume}.pdf')
        image_folder = os.path.join(images_dir, volume)

        # Check if the image folder already exists, if so, skip this volume
        if os.path.exists(image_folder) and os.listdir(image_folder):
            print(f"Volume '{volume}' already processed. Skipping.")
            continue

        print(f"Processing volume '{volume}'...")

        # Create a folder for the images
        os.makedirs(image_folder, exist_ok=True)

        # Download the PDF
        try:
            print(f"  Downloading PDF from {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"  PDF saved to {pdf_path}")
        except requests.exceptions.RequestException as e:
            print(f"  Error downloading {url}: {e}")
            # Clean up empty image folder if download fails
            if not os.listdir(image_folder):
                os.rmdir(image_folder)
            continue

        # Convert PDF to images
        try:
            print(f"  Converting {pdf_path} to images...")
            doc = fitz.open(pdf_path)
            if not doc.page_count:
                print(f"  Warning: PDF '{pdf_path}' has no pages.")
                doc.close()
                continue
                
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=300)
                output_image_path = os.path.join(image_folder, f'{page_num + 1}.png')
                pix.save(output_image_path)
            
            print(f"  Saved {doc.page_count} pages as images in {image_folder}")
            doc.close()
        except Exception as e:
            print(f"  Error converting {pdf_path} to images: {e}")
            continue

if __name__ == '__main__':
    download_and_convert_pdfs('urls.csv')
