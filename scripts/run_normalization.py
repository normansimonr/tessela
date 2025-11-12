import argparse
import os
import pandas as pd
from tqdm import tqdm

# Assuming the script is run from the root of the project
from src.data_loader import load_data, filter_septuagint
from src.normalization_service import normalize_text

def main(args):
    """
    Main function to run the normalization process.
    """
    print("Starting normalization process...")

    # Define file paths
    # In a real app, these would be more robustly handled
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
        print(f"Processing {source_name}...")
        try:
            df = load_data(file_path)

            # Apply filtering for Septuagint
            if source_name == "septuagint":
                df = filter_septuagint(df)

            # Normalize text for each row
            normalized_texts = []
            for text in tqdm(df['text'], desc=f"Normalizing {source_name}"):
                propositions = normalize_text(text, prompt_path)
                normalized_texts.append(propositions)
            
            df['normalization'] = normalized_texts

            # Save the processed dataframe
            df.to_csv(output_files[source_name], index=False)
            print(f"Successfully processed and saved {output_files[source_name]}")

        except FileNotFoundError:
            print(f"Warning: Source file not found at {file_path}. Skipping.")
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

    print("Normalization process finished.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the biblical text normalization process.")
    # We can add arguments here in the future, e.g., for input/output dirs
    args = parser.parse_args()
    main(args)
