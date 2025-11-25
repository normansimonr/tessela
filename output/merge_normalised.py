
import pandas as pd
import numpy as np

# Define file paths
masoretic_file = 'masoretic_normalised_hebrew.csv'
septuagint_file = 'septuagint_normalised.csv'
mapping_file = '../data/bible_versification_mapping_atomic.csv'
output_file = 'masoretic_septuagint_normalised.csv'

# Load the CSV files
masoretic_df = pd.read_csv(masoretic_file)
septuagint_df = pd.read_csv(septuagint_file).drop_duplicates()
mapping_df = pd.read_csv(mapping_file)

# Prepare the mapping DataFrame
def parse_ref(df, book_col, ref_col):
    # a copy is created to avoid SettingWithCopyWarning
    df = df.copy()
    # Safely split the 'ref_col' into 'Chapter' and 'Verse'
    ref_split = df[ref_col].str.split(':', n=1, expand=True)
    df[book_col + '_Chapter'] = pd.to_numeric(ref_split[0], errors='coerce')
    df[book_col + '_Verse'] = pd.to_numeric(ref_split[1], errors='coerce')
    return df

mapping_df = parse_ref(mapping_df, 'JPS', 'JPS_Ref')
mapping_df = parse_ref(mapping_df, 'LXX', 'LXX_Ref')

# Prepare the masoretic and septuagint DataFrames for merging
masoretic_df.rename(columns={'book_name': 'JPS_Book', 'chapter': 'JPS_Chapter', 'verse': 'JPS_Verse'}, inplace=True)
septuagint_df.rename(columns={'book_name': 'LXX_Book', 'chapter': 'LXX_Chapter', 'verse': 'LXX_Verse'}, inplace=True)

# Convert chapter and verse columns to numeric in masoretic and septuagint dataframes
masoretic_df['JPS_Chapter'] = pd.to_numeric(masoretic_df['JPS_Chapter'], errors='coerce')
masoretic_df['JPS_Verse'] = pd.to_numeric(masoretic_df['JPS_Verse'], errors='coerce')
septuagint_df['LXX_Chapter'] = pd.to_numeric(septuagint_df['LXX_Chapter'], errors='coerce')
septuagint_df['LXX_Verse'] = pd.to_numeric(septuagint_df['LXX_Verse'], errors='coerce')

# Inner merge mapping with septuagint
merged_df = pd.merge(mapping_df, septuagint_df, on=['LXX_Book', 'LXX_Chapter', 'LXX_Verse'], how='inner')

# Inner merge the result with masoretic
merged_df = pd.merge(merged_df, masoretic_df, on=['JPS_Book', 'JPS_Chapter', 'JPS_Verse'], how='inner')

# Select and rename columns for the final output
merged_df = merged_df.rename(columns={
    'JPS_Book': 'book_name',
    'JPS_Chapter': 'chapter',
    'JPS_Verse': 'verse',
    'text_x': 'septuagint_text',
    'normalization_x': 'septuagint_normalization',
    'text_y': 'masoretic_text',
    'normalization_y': 'masoretic_normalization'
})

# Define the final columns based on the new names
final_columns = [
    'book_name',
    'chapter',
    'verse',
    'masoretic_text',
    'septuagint_text',
    'masoretic_normalization',
    'septuagint_normalization'
]

# Ensure all final columns exist, fill with NaN if they don't
for col in final_columns:
    if col not in merged_df.columns:
        merged_df[col] = np.nan

# Select and reorder the final columns
final_df = merged_df[final_columns]

# Save the final DataFrame to CSV
final_df.to_csv(output_file, index=False)

print(f"Successfully merged files and saved to {output_file}")
