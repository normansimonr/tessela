
import pandas as pd
import re

def create_book_mappings(mapping_df, masoretic_df, septuagint_df):
    """
    Dynamically creates a mapping of book names to a standard abbreviation.
    """
    book_mappings = {}

    # Create mappings from the mapping file
    for _, row in mapping_df.iterrows():
        if pd.notna(row['Standard_Book']):
            if pd.notna(row['JPS_Book']):
                book_mappings[row['JPS_Book']] = row['Standard_Book']
            if pd.notna(row['LXX_Book']):
                book_mappings[row['LXX_Book']] = row['Standard_Book']

    # Add mappings for books in masoretic and septuagint files
    for book in masoretic_df['book_name'].unique():
        if book not in book_mappings:
            # Assuming the book name is already an abbreviation
            book_mappings[book] = book
            
    for book in septuagint_df['book_name'].unique():
        # For septuagint, we need to find its standard abbreviation from the mapping file
        # This part is tricky without some existing mapping. We will rely on the mapping file part above.
        # and add a few manual ones for completion
        pass

    # Add manual mappings for abbreviations and inconsistencies found
    # This is still necessary for names not perfectly aligned in the mapping file
    additional_mappings = {
        'Gen': 'GEN', 'Exo': 'EXO', 'Lev': 'LEV', 'Num': 'NUM', 'Deu': 'DEU',
        'Jos': 'JOS', 'Jdg': 'JDG', 'Rut': 'RUT', '1Sa': '1SA', '2Sa': '2SA',
        '1Ki': '1KI', '2Ki': '2KI', '1Ch': '1CH', '2Ch': '2CH', 'Ezr': 'EZR',
        'Neh': 'NEH', 'Est': 'EST', 'Job': 'JOB', 'Psa': 'PSA', 'Pro': 'PRO',
        'Ecc': 'ECC', 'Sng': 'SNG', 'Isa': 'ISA', 'Jer': 'JER', 'Lam': 'LAM',
        'Ezk': 'EZK', 'Dan': 'DAN', 'Hos': 'HOS', 'Jol': 'JOL', 'Amo': 'AMO',
        'Oba': 'OBA', 'Jon': 'JON', 'Mic': 'MIC', 'Nah': 'NAH', 'Hab': 'HAB',
        'Zep': 'ZEP', 'Hag': 'HAG', 'Zec': 'ZEC', 'Mal': 'MAL',
        'Esg': 'EST', 'SOL': 'SNG', 'EZE': 'EZK', 'JOE': 'JOL', 'Nam': 'NAH',
        'Daniel (Old Greek)': 'DAN', 'Man': 'MAN', 'Sus': 'SUS', 'Bel': 'BEL',
        'Tob': 'TOB', 'Sir': 'SIR', 'Jdt': 'JDT', '1Es': '1ES', 'Wis': 'WIS',
        'Bar': 'BAR', 'Lje': 'LJE', '2Es': '2ES', '4Ma': '4MA', '2Ma': '2MA',
        'Joshua (Vaticanus)': 'JOS', 'Judges (Vaticanus)': 'JDG',
        '1 Chronicles': '1CH', '2 Chronicles': '2CH', 'Song of Songs': 'SNG',
        '1 Kings': '1KI', '2 Kings': '2KI', '1 Samuel': '1SA', '2 Samuel': '2SA',
        '3 Kings': '1KI', '4 Kings': '2KI', '1 Paralipomenon': '1CH', '2 Paralipomenon': '2CH',
        '2 Esdras': 'NEH', 'Ade': 'EST', 'Psalm': 'PSA',
    }
    book_mappings.update(additional_mappings)
    
    return book_mappings

def clean_verse(verse):
    """
    Cleans verse numbers by taking only the numeric part.
    Handles floats by converting to int first, and subverses by removing non-digits.
    """
    if pd.isna(verse):
        return None
    s_verse = str(verse)
    # Handle floats like "10.0" -> "10"
    if '.' in s_verse:
        s_verse = s_verse.split('.')[0]
    # Remove any non-digit characters (for subverses like "1!a" -> "1")
    return re.sub(r'\D', '', s_verse)

# Load the datasets
masoretic_df = pd.read_csv("masoretic_normalised_hebrew.csv")
septuagint_df = pd.read_csv("septuagint_normalised.csv")
mapping_df = pd.read_csv("../data/bible_versification_mapping_atomic.csv")

book_mappings = create_book_mappings(mapping_df, masoretic_df, septuagint_df)


# Prepare Masoretic DataFrame
masoretic_df['book_abbr'] = masoretic_df['book_name'].map(book_mappings)
masoretic_df['verse_clean'] = masoretic_df['verse'].apply(clean_verse)
masoretic_df['chapter_clean'] = masoretic_df['chapter']
masoretic_df['key'] = masoretic_df['book_abbr'].astype(str) + '_' + masoretic_df['chapter_clean'].astype(str) + '_' + masoretic_df['verse_clean'].astype(str)

# Prepare Septuagint DataFrame
septuagint_df['book_abbr'] = septuagint_df['book_name'].map(book_mappings)
septuagint_df['verse_clean'] = septuagint_df['verse'].apply(clean_verse)
septuagint_df['chapter_clean'] = septuagint_df['chapter'].astype(float).astype(int) # Chapters might be floats
septuagint_df['key'] = septuagint_df['book_abbr'].astype(str) + '_' + septuagint_df['chapter_clean'].astype(str) + '_' + septuagint_df['verse_clean'].astype(str)

# Prepare Mapping DataFrame
mapping_df.dropna(subset=['JPS_Chapter', 'JPS_Verse', 'LXX_Chapter', 'LXX_Verse'], inplace=True)
mapping_df['jps_book_abbr'] = mapping_df['JPS_Book'].map(book_mappings)
mapping_df['jps_verse_clean'] = mapping_df['JPS_Verse'].apply(clean_verse)
mapping_df['jps_chapter_clean'] = mapping_df['JPS_Chapter'].astype(int)

mapping_df['lxx_book_abbr'] = mapping_df['LXX_Book'].map(book_mappings)
mapping_df['lxx_verse_clean'] = mapping_df['LXX_Verse'].apply(clean_verse)
mapping_df['lxx_chapter_clean'] = mapping_df['LXX_Chapter'].astype(int)

# Filter for rows where JPS and LXX versification is different
condition = (
    (mapping_df['jps_book_abbr'] != mapping_df['lxx_book_abbr']) |
    (mapping_df['jps_chapter_clean'] != mapping_df['lxx_chapter_clean']) |
    (mapping_df['jps_verse_clean'] != mapping_df['lxx_verse_clean'])
)
filtered_mapping_df = mapping_df[condition].copy()

# Create keys for merging
filtered_mapping_df['jps_key'] = filtered_mapping_df['jps_book_abbr'].astype(str) + '_' + filtered_mapping_df['jps_chapter_clean'].astype(str) + '_' + filtered_mapping_df['jps_verse_clean'].astype(str)
filtered_mapping_df['lxx_key'] = filtered_mapping_df['lxx_book_abbr'].astype(str) + '_' + filtered_mapping_df['lxx_chapter_clean'].astype(str) + '_' + filtered_mapping_df['lxx_verse_clean'].astype(str)

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
