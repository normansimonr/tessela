import pandas as pd
import os

def distill_tov_csv():
    """
    Reads the detailed 'tov.csv' file (which is at the word level)
    and creates a 'distilled' version aggregated by verse.

    The output CSV will have one row per verse with a boolean flag
    indicating if any word in that verse has a potential difference.
    """
    # Define relative paths based on the script's location
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(project_root, 'data', 'intermediate_datasets', 'tov.csv')
    output_path = os.path.join(project_root, 'data', 'intermediate_datasets', 'tov_distilled.csv')

    print(f"Reading detailed TOV data from {input_path}...")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        print("Please run 'scripts/convert_lxx_tov_to_csv_unicode.py' first.")
        return

    # Ensure the potential_difference column is treated as boolean
    if df['potential_difference'].dtype != bool:
        df['potential_difference'] = df['potential_difference'].astype(str).str.lower().map({'true': True, 'false': False})

    print("Aggregating data by verse...")
    # Group by verse and check if any word within the verse has a potential difference
    distilled_df = df.groupby(['book_name', 'chapter', 'verse'])['potential_difference'].any().reset_index()

    # Rename the column as requested
    distilled_df.rename(columns={'potential_difference': 'potential_difference_verse'}, inplace=True)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Saving distilled data to {output_path}...")
    distilled_df.to_csv(output_path, index=False)
    print("Distillation complete.")

if __name__ == '__main__':
    distill_tov_csv()
