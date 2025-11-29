import pandas as pd

# Load the datasets
masoretic_df = pd.read_csv("masoretic_normalised_hebrew.csv")
septuagint_df = pd.read_csv("septuagint_normalised.csv")
mapping_df = pd.read_csv("../data/bible_versification_mapping_atomic.csv")
mapping_df = mapping_df[["JPS_Book", "JPS_Chapter", "JPS_Verse", "LXX_Book", "LXX_Chapter", "LXX_Verse"]]


masoretic_df["verse"] = masoretic_df["verse"].astype(str)
mapping_df["JPS_Verse"] = mapping_df["JPS_Verse"].astype(str)

septuagint_df["verse"] = septuagint_df["verse"].astype(str)
mapping_df["LXX_Verse"] = mapping_df["LXX_Verse"].astype(str)

# Merge

masoretic_mapping = pd.merge(mapping_df, masoretic_df, left_on=["JPS_Book", "JPS_Chapter", "JPS_Verse"], right_on=["book_name", "chapter", "verse"], suffixes=["_mapping", "_JPS"])

masoretic_mapping.to_csv("temp.csv")

masoretic_mapping_septuagint = pd.merge(masoretic_mapping, septuagint_df, left_on=["LXX_Book", "LXX_Chapter", "LXX_Verse"], right_on=["book_name", "chapter", "verse"])

print(masoretic_mapping_septuagint)

exit()

# Merge mapping with masoretic
merged_df = pd.merge(filtered_mapping_df, masoretic_df, left_on='jps_key', right_on='key', how='left')

# Merge result with septuagint
merged_df = pd.merge(merged_df, septuagint_df, left_on='lxx_key', right_on='key', how='left', suffixes=('_masoretic', '_septuagint'))

# Select and rename columns for the final output
final_df = merged_df[[
    'Standard_Book', 'Standard_Chapter', 'Standard_Verse',
    'JPS_Book', 'JPS_Chapter', 'JPS_Verse', 'text_masoretic', 'normalization_masoretic',
    'LXX_Book', 'LXX_Chapter', 'LXX_Verse', 'text_septuagint', 'normalization_septuagint'
]].copy()

# Remove duplicate mappings that might result in identical rows
final_df.drop_duplicates(inplace=True)

# Save the merged dataframe
final_df.to_csv("masoretic_septuagint_normalised.csv", index=False)

print("Merging complete. Output saved to masoretic_septuagint_normalised.csv")
