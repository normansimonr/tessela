import csv
import re
import sys

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILENAME = "TVTMS - Translators Versification Traditions with Methodology for Standardisation for Eng+Heb+Lat+Grk+Others - STEPBible.org CC BY.txt"
OUTPUT_FILENAME = "bible_versification_mapping.csv"

# ==========================================
# BOOK NAME MAPPINGS
# ==========================================

# Map USFM (Dataset Internal) -> User's JPS Names
USFM_TO_JPS = {
    'Gen': 'GEN', 'Exo': 'EXO', 'Lev': 'LEV', 'Num': 'NUM', 'Deu': 'DEU',
    'Jos': 'JOS', 'Jdg': 'JDG', 'Rut': 'RUT', 
    '1Sa': '1SA', '2Sa': '2SA', '1Ki': '1KI', '2Ki': '2KI', 
    '1Ch': '1CH', '2Ch': '2CH', 'Ezr': 'EZR', 'Neh': 'NEH', 'Est': 'EST',
    'Job': 'JOB', 'Psa': 'PSA', 'Pro': 'PRO', 'Ecc': 'ECC', 'Sng': 'SOL',
    'Isa': 'ISA', 'Jer': 'JER', 'Lam': 'LAM', 'Ezk': 'EZE', 'Dan': 'DAN',
    'Hos': 'HOS', 'Jol': 'JOE', 'Amo': 'AMO', 'Oba': 'OBA', 'Jon': 'JON',
    'Mic': 'MIC', 'Nah': 'NAH', 'Hab': 'HAB', 'Zep': 'ZEP', 'Hag': 'HAG',
    'Zec': 'ZEC', 'Mal': 'MAL'
}

# Map USFM (Dataset Internal) -> User's Vulgate Names
USFM_TO_VULGATE = {
    'Gen': 'Genesis', 'Exo': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers', 'Deu': 'Deuteronomy',
    'Jos': 'Josue', 'Jdg': 'Judges', 'Rut': 'Ruth', 
    '1Sa': '1 Kings', '2Sa': '2 Kings', '1Ki': '3 Kings', '2Ki': '4 Kings', 
    '1Ch': '1 Paralipomenon', '2Ch': '2 Paralipomenon', 'Ezr': '1 Esdras', 'Neh': '2 Esdras', 'Est': 'Esther',
    'Job': 'Job', 'Psa': 'Psalms', 'Pro': 'Proverbs', 'Ecc': 'Ecclesiastes', 'Sng': 'Canticle of Canticles',
    'Isa': 'Isaias', 'Jer': 'Jeremias', 'Lam': 'Lamentations of Jeremias', 'Ezk': 'Ezechiel', 'Dan': 'Daniel',
    'Hos': 'Osee', 'Jol': 'Joel', 'Amo': 'Amos', 'Oba': 'Abdias', 'Jon': 'Jonas', 'Mic': 'Micheas',
    'Nah': 'Nahum', 'Hab': 'Habacuc', 'Zep': 'Sophonias', 'Hag': 'Aggeus', 'Zec': 'Zacharias', 'Mal': 'Malachias'
}

# Map USFM (Dataset Internal) -> User's LXX Names
USFM_TO_LXX = {
    'Gen': 'Genesis', 'Exo': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers', 'Deu': 'Deuteronomy',
    'Jos': 'Joshua (Vaticanus)', 'Jdg': 'Judges (Vaticanus)', 'Rut': 'Ruth', 
    '1Sa': '1 Samuel', '2Sa': '2 Samuel', '1Ki': '1 Kings', '2Ki': '2 Kings', 
    '1Ch': '1 Chronicles', '2Ch': '2 Chronicles', 'Ezr': 'Ezra', 'Neh': 'Nehemiah', 'Est': 'Esther',
    'Job': 'Job', 'Psa': 'Psalms', 'Pro': 'Proverbs', 'Ecc': 'Ecclesiastes', 'Sng': 'Song of Songs',
    'Isa': 'Isaiah', 'Jer': 'Jeremiah', 'Lam': 'Lamentations', 'Ezk': 'Ezekiel', 'Dan': 'Daniel (Old Greek)',
    'Hos': 'Hosea', 'Jol': 'Joel', 'Amo': 'Amos', 'Oba': 'Obadiah', 'Jon': 'Jonah', 'Mic': 'Micah',
    'Nah': 'Nahum', 'Hab': 'Habakkuk', 'Zep': 'Zephaniah', 'Hag': 'Haggai', 'Zec': 'Zechariah', 'Mal': 'Malachi'
}

# ==========================================
# LOGIC
# ==========================================

def parse_dataset(filename):
    """
    Parses the TVTMS text file.
    Returns a dictionary keyed by StandardRef (KJV) containing the mapped refs for each tradition.
    Structure:
    data = {
        "Gen.31:55": {
            "Hebrew": "Gen.32:1", 
            "Latin": "Gen.31:55",
            "Greek": "Gen.31:55"
        },
        ...
    }
    """
    data = {}
    data_started = False

    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f, delimiter='\t')
            
            for row in reader:
                # Detect start of the expanded data section
                if not data_started:
                    if row and "#DataStart(Expanded)" in row[0]:
                        data_started = True
                    continue
                
                # Skip headers or empty lines
                if not row or row[0].startswith("'") or row[0].startswith("SourceType"):
                    continue
                
                if len(row) < 3: continue

                source_type = row[0]
                source_ref = row[1]
                std_ref = row[2]

                # Initialize the Standard Reference key if it doesn't exist
                if std_ref not in data:
                    data[std_ref] = {}

                # 1. Check for Hebrew Mapping
                # "Eng-KJV" usually implies Hebrew follows KJV unless otherwise stated,
                # but we specifically look for "Hebrew" in the type or implicit KJV alignment.
                if "Hebrew" in source_type:
                    data[std_ref]['Hebrew'] = source_ref
                elif "Eng-KJV" in source_type and "Latin" not in source_type and "Greek" not in source_type:
                    # Base alignment line
                    data[std_ref]['Hebrew'] = source_ref

                # 2. Check for Latin Mapping
                if "Latin" in source_type:
                    data[std_ref]['Latin'] = source_ref

                # 3. Check for Greek Mapping
                if "Greek" in source_type:
                    data[std_ref]['Greek'] = source_ref

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
        
    return data

def format_reference(ref_string, book_map, clean_subverses=True):
    """
    Converts internal Ref (Gen.32:1!a) to Output format (BookName, 32:1).
    Returns a tuple (BookName, Reference).
    """
    # Handle "Absent" or special codes
    if "Absent" in ref_string:
        return ("ABSENT", "ABSENT")
    
    # Strip !a, !b subverses for cleaner CSV if requested
    # (The pipeline usually wants to know the main verse number)
    clean_ref = ref_string
    if clean_subverses:
        clean_ref = ref_string.split('!')[0] # Remove !a, !b
        clean_ref = clean_ref.split('[')[0]  # Remove [notes]

    # Regex to separate Book from Chapter:Verse
    match = re.match(r"([1-3]?[A-Za-z]+)\.(\d+:\d+.*)", clean_ref)
    
    if not match:
        # Fallback for complex strings or ranges that didn't parse cleanly
        return ("Unknown", clean_ref)
        
    book_code = match.group(1)
    verse_part = match.group(2)
    
    # Look up the book name based on the target tradition (JPS/Vulgate/LXX)
    book_name = book_map.get(book_code)
    
    # If book isn't in the user's list (e.g. NT books), return internal code or None
    if not book_name:
        return (book_code, verse_part)
        
    return (book_name, verse_part)

def generate_csv(data, output_file):
    print(f"Processing {len(data)} mapping rules...")
    
    headers = [
        'Standard_Link_ID',     # The invariant ID (KJV) linking them
        'JPS_Book', 'JPS_Ref',
        'Vulgate_Book', 'Vulgate_Ref',
        'LXX_Book', 'LXX_Ref'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        # Iterate through all Standard IDs found in the dataset
        for std_id, traditions in data.items():
            
            # 1. Determine RAW references for each tradition
            # If explicit mapping exists, use it.
            # If NOT, assume it matches the Standard ID (Default behavior for versification maps)
            raw_hebrew = traditions.get('Hebrew', std_id)
            raw_latin = traditions.get('Latin', std_id)
            raw_greek = traditions.get('Greek', std_id)

            # 2. Format for JPS
            jps_book, jps_vers = format_reference(raw_hebrew, USFM_TO_JPS)
            
            # Filter: If JPS Book is not in user's list (e.g. New Testament), skip this row
            # (Since user only provided OT lists, we assume they only want OT output)
            if jps_book not in USFM_TO_JPS.values() and jps_book != "ABSENT":
                 # Check if it's actually an OT book that just failed mapping?
                 # No, strictly filter to ensure only requested books appear.
                 # Use raw_hebrew book code to check if it's NT (e.g. Mat, Rev)
                 if raw_hebrew.split('.')[0] not in USFM_TO_JPS:
                     continue

            # 3. Format for Vulgate
            vul_book, vul_vers = format_reference(raw_latin, USFM_TO_VULGATE)
            
            # 4. Format for LXX
            lxx_book, lxx_vers = format_reference(raw_greek, USFM_TO_LXX)

            # 5. Write Row
            writer.writerow([
                std_id,
                jps_book, jps_vers,
                vul_book, vul_vers,
                lxx_book, lxx_vers
            ])
            
    print(f"Successfully created '{output_file}'")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("--- Bible Versification Pipeline Converter ---")
    mapped_data = parse_dataset(INPUT_FILENAME)
    generate_csv(mapped_data, OUTPUT_FILENAME)
