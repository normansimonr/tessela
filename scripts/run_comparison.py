import argparse
import concurrent.futures
import json
import logging
import os

import pandas as pd
from tqdm import tqdm

# Assuming the script is run from the root of the project
from src.data_loader import load_data
from src.normalization_service import compare_verses

# Define the maximum number of concurrent workers for API calls
MAX_WORKERS = 5

def setup_logging():
    """Sets up the logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("comparison.log"),
            logging.StreamHandler()
        ]
    )

def main(args):
    """
    Main function to run the comparison process.
    """
    setup_logging()
    logging.info("Starting comparison process...")

    # Define file paths
    input_file = 'output/masoretic_septuagint.csv'
    output_dir = 'comparisons'
    output_file_path = os.path.join(output_dir, "jps_brenton.csv")
    prompt_path = 'prompts/comparison_prompt.txt'

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        df = load_data(input_file)
        logging.info(f"Initial DataFrame size: {len(df)}")

        processed_verses = set()

        # Check for existing output file to resume
        if os.path.exists(output_file_path):
            logging.info("Output file found. Resuming...")
            processed_df = pd.read_csv(output_file_path)
            # Create a unique identifier for each verse in the processed DataFrame
            processed_df['unique_verse_id'] = processed_df.apply(
                lambda row: (row['book_name'], row['chapter'], row['verse']), axis=1
            )
            processed_verses = set(processed_df['unique_verse_id'])
            logging.info(f"Number of processed verses: {len(processed_verses)}")

            # Create a unique identifier for each verse in the original DataFrame
            df['unique_verse_id'] = df.apply(
                lambda row: (row['book_name'], row['chapter'], row['verse']), axis=1
            )
            df_to_process = df[~df['unique_verse_id'].isin(processed_verses)]
            # Drop the temporary unique_verse_id column from df
            df = df.drop(columns=['unique_verse_id'])
        else:
            df_to_process = df

        logging.info(f"DataFrame to process size: {len(df_to_process)}")
        if df_to_process.empty:
            logging.info("All verses have already been processed. Skipping.")
            return

        # Initialize output file if it doesn't exist
        if not os.path.exists(output_file_path):
            df_to_process.reindex(columns=list(df.columns) + ['comparison_veredict']).to_csv(output_file_path, mode='w', header=True, index=False)


        # Process each row
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_row = {
                executor.submit(compare_verses, row['normalization_JPS'], row['normalization_LXX'], prompt_path): row
                for index, row in df_to_process.iterrows()
            }

            for future in tqdm(
                concurrent.futures.as_completed(future_to_row),
                total=len(df_to_process),
                desc="Comparing verses"
            ):
                original_row = future_to_row[future]
                try:
                    comparison_veredict = future.result()
                    original_row['comparison_veredict'] = json.dumps(comparison_veredict)
                    pd.DataFrame([original_row]).to_csv(output_file_path, mode='a', header=False, index=False)
                except Exception as exc:
                    logging.error(f"Verse {original_row['book_name']} {original_row['chapter']}:{original_row['verse']} generated an exception: {exc}")
                    original_row['comparison_veredict'] = json.dumps([])
                    pd.DataFrame([original_row]).to_csv(output_file_path, mode='a', header=False, index=False)

        logging.info(f"Successfully processed and saved all new verses to {output_file_path}")

    except FileNotFoundError:
        logging.error(f"Input file not found at {input_file}. Exiting.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    logging.info("Comparison process finished.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the biblical text comparison process.")
    # We can add arguments here in the future, e.g., for input/output dirs
    args = parser.parse_args()
    main(args)
