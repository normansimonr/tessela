import pandas as pd

masoretic_df = pd.read_csv('output/masoretic_normalised_hebrew.csv')
septuagint_df = pd.read_csv('output/septuagint_normalised.csv')
mapping_df = pd.read_csv('data/bible_versification_mapping_atomic.csv')

masoretic_books = set(masoretic_df['book_name'].unique())
jps_books = set(mapping_df['JPS_Book'].dropna().unique())

print("--- Masoretic vs JPS ---")
print("Books in masoretic_normalised_hebrew.csv but not in mapping's JPS_Book:")
print(sorted(list(masoretic_books - jps_books)))
print("\nBooks in mapping's JPS_Book but not in masoretic_normalised_hebrew.csv:")
print(sorted(list(jps_books - masoretic_books)))


septuagint_books = set(septuagint_df['book_name'].unique())
lxx_books = set(mapping_df['LXX_Book'].dropna().unique())

print("\n--- Septuagint vs LXX ---")
print("Books in septuagint_normalised.csv but not in mapping's LXX_Book:")
print(sorted(list(septuagint_books - lxx_books)))
print("\nBooks in mapping's LXX_Book but not in septuagint_normalised.csv:")
print(sorted(list(lxx_books - septuagint_books)))

# Also check for the "Esg" case
print("\n--- Checking for 'Esg' ---")
if 'Esg' in jps_books:
    print("'Esg' is in JPS_Book column of the mapping file.")
if 'Esg' not in masoretic_books:
    print("'Esg' is NOT in book_name column of masoretic_normalised_hebrew.csv.")
