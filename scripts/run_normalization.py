import argparse
import os
import pandas as pd
from tqdm import tqdm
import logging

# Assuming the script is run from the root of the project
from src.data_loader import load_data, filter_septuagint
from src.normalization_service import normalize_text

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

            # Normalize text for each row
            normalized_texts = []
            for text in tqdm(df_to_process['text'], desc=f"Normalizing {source_name}"):
                propositions = normalize_text(text, prompt_path)
                normalized_texts.append(propositions)
            
            df_to_process['normalization'] = normalized_texts

            # Save the processed dataframe
            df_to_process.to_csv(
                output_file_path, 
                mode='a', 
                header=not os.path.exists(output_file_path), 
                index=False
            )
            logging.info(f"Successfully processed and saved {output_files[source_name]}")

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
