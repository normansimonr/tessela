import argparse
import os
import pandas as pd
from tqdm import tqdm
import logging
import concurrent.futures

# Assuming the script is run from the root of the project
from src.data_loader import load_data, filter_septuagint
from src.normalization_service import normalize_text

# Define the maximum number of concurrent workers for API calls
MAX_WORKERS = 10

def setup_logging():
    """Sets up the logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("normalization.log"),
            logging.StreamHandler()
        ]
    )

def main(args):
    """
    Main function to run the normalization process.
    """
    setup_logging()
    logging.info("Starting normalization process...")

    # Define file paths
    data_dir = 'data'
    output_dir = 'output'
    prompt_path = 'prompts/normalization_prompt.txt'

    source_files = {
        "masoretic": os.path.join(data_dir, "masoretic.csv"),
        "vulgate": os.path.join(data_dir, "vulgate.csv"),
        "septuagint": os.path.join(data_dir, "septuagint.csv"),
    }

    output_files = {
        "masoretic": os.path.join(output_dir, "masoretic_normalised.csv"),
        "vulgate": os.path.join(output_dir, "vulgate_normalised.csv"),
        "septuagint": os.path.join(output_dir, "septuagint_normalised.csv"),
    }

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each source file
    for source_name, file_path in source_files.items():
        logging.info(f"Processing {source_name}...")
        try:
            df = load_data(file_path)

            # Apply filtering for Septuagint
            if source_name == "septuagint":
                df = filter_septuagint(df)

            output_file_path = output_files[source_name]
            processed_verses = set()

            # Check for existing output file to resume
            if os.path.exists(output_file_path):
                logging.info(f"Output file found for {source_name}. Resuming...")
                processed_df = pd.read_csv(output_file_path)
                processed_verses = set(processed_df['text'])
                df_to_process = df[~df['text'].isin(processed_verses)]
            else:
                df_to_process = df

            if df_to_process.empty:
                logging.info(f"All verses in {source_name} have already been processed. Skipping.")
                continue

            # Normalize text for each row concurrently
            normalized_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Submit tasks to the executor
                future_to_verse = {
                    executor.submit(normalize_text, text, prompt_path): text
                    for text in df_to_process['text']
                }
                
                # Process results as they complete
                for future in tqdm(
                    concurrent.futures.as_completed(future_to_verse), 
                    total=len(df_to_process), 
                    desc=f"Normalizing {source_name}"
                ):
                    verse_text = future_to_verse[future]
                    try:
                        propositions = future.result()
                        normalized_results.append({'text': verse_text, 'normalization': propositions})
                    except Exception as exc:
                        logging.error(f"'{verse_text}' generated an exception: {exc}")
                        normalized_results.append({'text': verse_text, 'normalization': []}) # Append empty list on error
            
            # Convert results to DataFrame and merge with original
            if normalized_results:
                new_normalized_df = pd.DataFrame(normalized_results)
                # Ensure the order is maintained if needed, or just append
                # For appending, order doesn't strictly matter as much as having all data
                
                # If output file exists, append without header, otherwise write with header
                if os.path.exists(output_file_path):
                    new_normalized_df.to_csv(output_file_path, mode='a', header=False, index=False)
                else:
                    new_normalized_df.to_csv(output_file_path, mode='w', header=True, index=False)
                
                logging.info(f"Successfully processed and saved {len(new_normalized_df)} new verses to {output_files[source_name]}")
            else:
                logging.info(f"No new verses processed for {source_name}.")

        except FileNotFoundError:
            logging.warning(f"Source file not found at {file_path}. Skipping.")
        except Exception as e:
            logging.error(f"An error occurred while processing {file_path}: {e}")

    logging.info("Normalization process finished.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the biblical text normalization process.")
    # We can add arguments here in the future, e.g., for input/output dirs
    args = parser.parse_args()
    main(args)
