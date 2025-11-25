import pandas as pd

# 1. Read the CSV
jps = pd.read_csv("masoretic_normalised.csv").dropna(subset=["normalization"])

# Optional: Only drop if you strictly require normalization data
# jps = jps.dropna(subset=["normalization"]) 

# 2. Ensure fallback columns exist
if "chapter" not in jps.columns:
    jps["chapter"] = pd.NA
if "verse" not in jps.columns:
    jps["verse"] = pd.NA

# 3. Define Regex
# Robust regex: accepts hyphen, en-dash, em-dash and optional spaces
pattern = r"\(\s*(\d+)\s*[–—-]\s*(\d+)\s*\)"

# 4. Extract from the TEXT column, not normalization
# We force astype(str) just in case there are non-string objects
text_str = jps["text"].astype(str)

extracted = text_str.str.extract(pattern, expand=True)

# 5. Convert extracted groups to numeric (NaN when missing)
ex_chapter = pd.to_numeric(extracted[0], errors="coerce")
ex_verse   = pd.to_numeric(extracted[1], errors="coerce")

# 6. Convert existing chapter/verse to numeric
orig_chapter = pd.to_numeric(jps["chapter"], errors="coerce")
orig_verse   = pd.to_numeric(jps["verse"], errors="coerce")

# 7. Update logic: Use extracted if found, otherwise keep original
# combine_first prefers the calling object (ex_chapter) if it's not null
final_chapter = ex_chapter.combine_first(orig_chapter)
final_verse   = ex_verse.combine_first(orig_verse)

# 8. Assign back to DataFrame using Int64 to handle NaNs cleanly
jps["chapter"] = final_chapter.astype("Int64")
jps["verse"]   = final_verse.astype("Int64")

# 9. Sanity check
mask_changed = (~ex_chapter.isna()) & (ex_chapter != orig_chapter.fillna(-99999))
if mask_changed.any():
    print(f"Success! Updated {mask_changed.sum()} rows.")
    print("Examples:")
    print(jps.loc[mask_changed, ["text", "chapter", "verse"]].head(5))
else:
    print("No patterns found to update.")

jps.to_csv("masoretic_normalised_hebrew.csv", index=False)
