import pandas as pd

# Load the datasets
masoretic_df = pd.read_csv("masoretic_normalised_hebrew.csv")
septuagint_df = pd.read_csv("septuagint_normalised.csv")
mapping_df = pd.read_csv("../data/bible_versification_mapping_atomic.csv")
mapping_df = mapping_df[["JPS_Book", "JPS_Chapter", "JPS_Verse", "LXX_Book", "LXX_Chapter", "LXX_Verse"]]


masoretic_df["verse"] = masoretic_df["verse"].astype(str)
mapping_df["JPS_Verse"] = mapping_df["JPS_Verse"].astype(str)

septuagint_df["book_name"] = septuagint_df["book_name"].astype(str)
septuagint_df["chapter"] = septuagint_df["chapter"].astype(str)
septuagint_df["verse"] = septuagint_df["verse"].astype(str)
mapping_df["LXX_Book"] = mapping_df["LXX_Book"].astype(str)
mapping_df["LXX_Chapter"] = mapping_df["LXX_Chapter"].astype(str)
mapping_df["LXX_Verse"] = mapping_df["LXX_Verse"].astype(str)

# Merge

masoretic_mapping = pd.merge(mapping_df, masoretic_df, left_on=["JPS_Book", "JPS_Chapter", "JPS_Verse"], right_on=["book_name", "chapter", "verse"])

masoretic_mapping = masoretic_mapping.drop(columns=["book_name", "chapter", "verse"])

septuagint_df = septuagint_df.rename(columns={"book_name":"LXX_Book", "chapter":"LXX_Chapter", "verse":"LXX_Verse"})
print(septuagint_df)

masoretic_mapping_septuagint = pd.merge(masoretic_mapping, septuagint_df, on=["LXX_Book", "LXX_Chapter", "LXX_Verse"], suffixes=["_JPS", "_LXX"], how="outer")

print(masoretic_mapping_septuagint)
masoretic_mapping_septuagint.to_csv("temp.csv")
