import pandas as pd

# Load the datasets
masoretic_df = pd.read_csv("masoretic_normalised_hebrew.csv", dtype=str)
vulgate_df = pd.read_csv("vulgate_normalised.csv", dtype=str).drop_duplicates()
verse_map = pd.read_csv("../data/bible_versification_mapping_atomic.csv", dtype=str)

# The mapping dictionary for renaming the books
book_renaming_map = {
    "Genesis": "GEN",
    "Exodus": "EXO",
    "Leviticus": "LEV",
    "Numbers": "NUM",
    "Deuteronomy": "DEU",
    "Josue": "JOS",
    "Judges": "JDG",
    "Ruth": "RUT",
    "1 Kings": "1SA",
    "2 Kings": "2SA",
    "3 Kings": "1KI",
    "4 Kings": "2KI",
    "1 Paralipomenon": "1CH",
    "2 Paralipomenon": "2CH",
    "1 Esdras": "EZR",
    "2 Esdras": "NEH",
    "Esther": "EST",
    "Job": "JOB",
    "Psalms": "PSA",
    "Proverbs": "PRO",
    "Ecclesiastes": "ECC",
    "Canticle of Canticles": "SOL",
    "Isaias": "ISA",
    "Jeremias": "JER",
    "Lamentations of Jeremias": "LAM",
    "Ezechiel": "EZE",
    "Daniel": "DAN",
    "Osee": "HOS",
    "Joel": "JOE",
    "Amos": "AMO",
    "Abdias": "OBA",
    "Jonas": "JON",
    "Micheas": "MIC",
    "Nahum": "NAH",
    "Habacuc": "HAB",
    "Sophonias": "ZEP",
    "Aggeus": "HAG",
    "Zacharias": "ZEC",
    "Malachias": "MAL"
}


# Prepare verse_map

verse_map = verse_map[["JPS_Book", "JPS_Chapter", "JPS_Verse", "Vulgate_Book", "Vulgate_Chapter", "Vulgate_Verse"]]


verse_map['JPS_Verse'] = verse_map['JPS_Verse'].str.replace("!a", "").str.replace("!b", "").str.replace("!c", "").str.replace("!d", "")
verse_map['Vulgate_Verse'] = verse_map['Vulgate_Verse'].str.replace("!a", "").str.replace("!b", "").str.replace("!c", "").str.replace("!d", "")

verse_map["match"] = (
    (verse_map["JPS_Chapter"] == verse_map["Vulgate_Chapter"]) &
    (verse_map["JPS_Verse"] == verse_map["Vulgate_Verse"])
)

verse_map = verse_map[~verse_map["match"]]

# Prepare masoretic and vulgate

masoretic_df = masoretic_df.rename(columns={"book_name":"JPS_Book", "chapter":"JPS_Chapter", "verse":"JPS_Verse"})
vulgate_df = vulgate_df.rename(columns={"book_name":"Vulgate_Book", "chapter":"Vulgate_Chapter", "verse":"Vulgate_Verse"})

# Merge masoretic and mapping

masoretic_and_atomic = pd.merge(masoretic_df, verse_map, on=["JPS_Book", "JPS_Chapter", "JPS_Verse"], how="outer")

# Inner join with Vulgate

masoretic_vulgate_inner = pd.merge(masoretic_and_atomic, vulgate_df, on=["Vulgate_Book", "Vulgate_Chapter", "Vulgate_Verse"], how="inner", suffixes=["_JPS", "_VUL"])

# Joining the remaining verses (which are the same coordinates with JPS)

missing = vulgate_df.merge(
    masoretic_vulgate_inner[["Vulgate_Book", "Vulgate_Chapter", "Vulgate_Verse"]],
    on=["Vulgate_Book", "Vulgate_Chapter", "Vulgate_Verse"],
    how="left",
    indicator=True
)

missing = missing[missing["_merge"] == "left_only"].drop(columns="_merge")
missing["Vulgate_Book"] = missing["Vulgate_Book"].map(book_renaming_map)
missing = missing.rename(columns={"Vulgate_Book":"JPS_Book", "Vulgate_Chapter":"JPS_Chapter", "Vulgate_Verse":"JPS_Verse"})

masoretic_vulgate_missing = pd.merge(masoretic_and_atomic, missing, on=["JPS_Book", "JPS_Chapter", "JPS_Verse"], how="outer", suffixes=["_JPS", "_VUL"])

# Concatenating both merges

masoretic_vulgate = pd.concat([masoretic_vulgate_inner, masoretic_vulgate_missing])
masoretic_vulgate["JPS_Chapter"] = masoretic_vulgate["JPS_Chapter"].astype(float)
masoretic_vulgate["JPS_Verse"] = masoretic_vulgate["JPS_Verse"].astype(float)
masoretic_vulgate = masoretic_vulgate.sort_values(by=["JPS_Book", "JPS_Chapter", "JPS_Verse"], ascending=True)

# Removing duplicates

masoretic_vulgate["duplicated"] = masoretic_vulgate.duplicated(subset=["JPS_Book", "JPS_Chapter", "JPS_Verse"], keep=False)
masoretic_vulgate = masoretic_vulgate[~((masoretic_vulgate["duplicated"]) & (masoretic_vulgate["text_VUL"].isna()))]
masoretic_vulgate = masoretic_vulgate.drop_duplicates()
masoretic_vulgate = masoretic_vulgate.drop(columns=["match", "duplicated"])

print(masoretic_vulgate)

print(f"Matched Rows: {len(masoretic_vulgate)}")
masoretic_vulgate.to_csv("masoretic_vulgate.csv", index=False)
