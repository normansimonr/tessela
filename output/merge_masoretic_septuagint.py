import pandas as pd

# Load the datasets
masoretic_df = pd.read_csv("masoretic_normalised_hebrew.csv")
septuagint_df = pd.read_csv("septuagint_normalised.csv").drop_duplicates()

# The mapping dictionary for renaming the books
book_renaming_map = {
    '1 Chronicles': '1CH',
    '1 Kings': '1KI',
    '1 Samuel': '1SA',
    '2 Chronicles': '2CH',
    '2 Kings': '2KI',
    '2 Samuel': '2SA',
    'Amos': 'AMO',
    'Daniel (Old Greek)': 'DAN',
    'Deuteronomy': 'DEU',
    'Ecclesiastes': 'ECC',
    'Esther': 'EST',
    'Exodus': 'EXO',
    'Ezekiel': 'EZE',
    'Ezra': 'EZR',
    'Genesis': 'GEN',
    'Habakkuk': 'HAB',
    'Haggai': 'HAG',
    'Hosea': 'HOS',
    'Isaiah': 'ISA',
    'Jeremiah': 'JER',
    'Job': 'JOB',
    'Joel': 'JOE',
    'Jonah': 'JON',
    'Joshua (Vaticanus)': 'JOS',
    'Judges (Vaticanus)': 'JDG',
    'Lamentations': 'LAM',
    'Leviticus': 'LEV',
    'Malachi': 'MAL',
    'Micah': 'MIC',
    'Nahum': 'NAH',
    'Nehemiah': 'NEH',
    'Numbers': 'NUM',
    'Obadiah': 'OBA',
    'Proverbs': 'PRO',
    'Psalms': 'PSA',
    'Ruth': 'RUT',
    'Song of Songs': 'SOL',
    'Zechariah': 'ZEC',
    'Zephaniah': 'ZEP'
}

# Apply the renaming to the 'book_name' column
septuagint_df['book_name'] = septuagint_df['book_name'].map(book_renaming_map)

masoretic_septuagint = pd.merge(masoretic_df, septuagint_df, on=["book_name", "chapter", "verse"], how="right", suffixes=["_JPS", "_LXX"])

print(f"Matched Rows: {len(masoretic_septuagint)}")
masoretic_septuagint.to_csv("masoretic_septuagint.csv", index=False)
