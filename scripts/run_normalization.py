import json
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
MAX_WORKERS = 1

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
            logging.info(f"Initial {source_name} DataFrame size: {len(df)}")

            # Apply filtering for Septuagint
            if source_name == "septuagint":
                df = filter_septuagint(df)

            output_file_path = output_files[source_name]
            logging.debug(f"Checking if output file exists: {output_file_path} -> {os.path.exists(output_file_path)}")
            processed_verses = set()

            # Check for existing output file to resume
            if os.path.exists(output_file_path):
                logging.info(f"Output file found for {source_name}. Resuming...")
                processed_df = pd.read_csv(output_file_path)
                # Create a unique identifier for each verse in the processed DataFrame
                processed_df['unique_verse_id'] = processed_df.apply(
                    lambda row: (row['book_name'], row['chapter'], row['verse'], row['text']), axis=1
                )
                # Convert 'normalization' column from string representation of list to actual list
                # Handle potential NaN values or malformed JSON strings
                processed_df['normalization_list'] = processed_df['normalization'].apply(
                    lambda x: json.loads(x) if pd.notna(x) and x.strip() else []
                )
                # Only consider verses with non-empty normalization results as processed
                processed_df_successful = processed_df[processed_df['normalization_list'].apply(lambda x: bool(x))]
                processed_verses = set(processed_df_successful['unique_verse_id'])
                logging.info(f"Number of processed verses for {source_name}: {len(processed_verses)}")

                # Create a unique identifier for each verse in the original DataFrame
                df['unique_verse_id'] = df.apply(
                    lambda row: (row['book_name'], row['chapter'], row['verse'], row['text']), axis=1
                )
                df_to_process = df[~df['unique_verse_id'].isin(processed_verses)]
                # Drop the temporary unique_verse_id column from df
                df = df.drop(columns=['unique_verse_id'])
            else:
                df_to_process = df

            logging.info(f"DataFrame to process for {source_name} size: {len(df_to_process)}")
            if df_to_process.empty:
                logging.info(f"All verses in {source_name} have already been processed. Skipping.")
                # Log verses that were in original df but not in processed_verses (if any)
                unprocessed_in_original = set(df['text']) - processed_verses
                if unprocessed_in_original:
                    logging.warning(f"Unexpected: {len(unprocessed_in_original)} verses from original {source_name} dataset were not found in processed_verses, but df_to_process is empty. Examples: {list(unprocessed_in_original)[:5]}")
                continue
            else:
                logging.info(f"Resuming processing for {source_name}. First 5 verses to process: {list(df_to_process['text'])[:5]}")

            # Initialize output file if it doesn't exist
            if not os.path.exists(output_file_path):
                pd.DataFrame(columns=['book_name', 'chapter', 'verse', 'text', 'normalization']).to_csv(output_file_path, mode='w', header=True, index=False)

            # Normalize text for each row concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Submit tasks to the executor
                future_to_row = {
                    executor.submit(normalize_text, row['book_name'], row['chapter'], row['verse'], row['text'], prompt_path): row
                    for index, row in df_to_process.iterrows()
                }

                # Process results as they complete and save incrementally
                for future in tqdm(
                    concurrent.futures.as_completed(future_to_row),
                    total=len(df_to_process),
                    desc=f"Normalizing {source_name}"
                ):
                    original_row = future_to_row[future]
                    try:
                        propositions = future.result()
                        result_df = pd.DataFrame([{
                            'book_name': original_row['book_name'],
                            'chapter': original_row['chapter'],
                            'verse': original_row['verse'],
                            'text': original_row['text'],
                            'normalization': json.dumps(propositions)
                        }])
                        result_df.to_csv(output_file_path, mode='a', header=False, index=False)
                    except Exception as exc:
                        logging.error(f"'{original_row['text']}' generated an exception: {exc}")
                        # Even on error, save an entry to mark it as processed (with empty normalization)
                        result_df = pd.DataFrame([{
                            'book_name': original_row['book_name'],
                            'chapter': original_row['chapter'],
                            'verse': original_row['verse'],
                            'text': original_row['text'],
                            'normalization': []
                        }])
                        result_df.to_csv(output_file_path, mode='a', header=False, index=False)

            logging.info(f"Successfully processed and saved all new verses to {output_files[source_name]}")
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
