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

#vulgate_df['book_name'] = vulgate_df['book_name'].map(book_renaming_map)

verse_map = verse_map[["Standard_Book", "Standard_Chapter", "Standard_Verse", "JPS_Book", "JPS_Chapter", "JPS_Verse", "Vulgate_Book", "Vulgate_Chapter", "Vulgate_Verse"]]

verse_map['Standard_Verse'] = verse_map['Standard_Verse'].str.replace("!a", "").str.replace("!b", "").str.replace("!c", "").str.replace("!d", "")
verse_map['JPS_Verse'] = verse_map['JPS_Verse'].str.replace("!a", "").str.replace("!b", "").str.replace("!c", "").str.replace("!d", "")
verse_map['Vulgate_Verse'] = verse_map['Vulgate_Verse'].str.replace("!a", "").str.replace("!b", "").str.replace("!c", "").str.replace("!d", "")

masoretic_and_atomic = pd.merge(masoretic_df, verse_map, left_on=["book_name", "chapter", "verse"], right_on=["JPS_Book", "JPS_Chapter", "JPS_Verse"], how="outer", suffixes=["_JPS", "_VUL"])

print(masoretic_and_atomic)

masoretic_vulgate = pd.merge(masoretic_and_atomic, vulgate_df, left_on=["JPS_Book", "Vulgate_Chapter", "Vulgate_Verse"], right_on = ["book_name", "chapter", "verse"], how="inner", suffixes=["_JPS", "_VUL"])

print(f"Matched Rows: {len(masoretic_vulgate)}")
masoretic_vulgate.to_csv("masoretic_vulgate.csv", index=False)
