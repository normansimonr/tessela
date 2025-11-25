import csv
import re
import sys

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILENAME = "TVTMS - Translators Versification Traditions with Methodology for Standardisation for Eng+Heb+Lat+Grk+Others - STEPBible.org CC BY.txt"
OUTPUT_FILENAME = "bible_versification_mapping_atomic.csv"

# ==========================================
# MAPPINGS (USFM -> USER FORMAT)
# ==========================================
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

USFM_TO_LXX = {
    'Gen': 'Genesis', 'Exo': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers', 'Deu': 'Deuteronomy',
    'Jos': 'Joshua (Vaticanus)', 'Jdg': 'Judges (Vaticanus)', 'Rut': 'Ruth', 
    '1Sa': '1 Samuel', '2Sa': '2 Samuel', '1Ki': '1 Kings', '2Ki': '2 Kings', 
    '1Ch': '1 Chronicles', '2Ch': '2 Chronicles', 'Ezr': 'Ezra', 'Neh': 'Nehemiah', 'Est': 'Esther',
    'Job': 'Job', 'Psa': 'Psalms', 'Pro': 'Proverbs', 'Ecc': 'Ecclesiastes', 'Sng': 'Song of Songs',
    'Isa': 'Isaiah', 'Jer': 'Jeremiah', 'Lam': 'Lamentations', 'Ezk': 'Ezekiel', 'Dan': 'Daniel (Old Greek)',
    'Hos': 'Hosea', 'Jol': 'Joel', 'Amo': 'Amos', 'Oba': 'Obadiah', 'Jon': 'Jonah', 'Mic': 'Micah',
    'Nah': 'Nahum', 'Hab': 'Habacuc', 'Zep': 'Zephaniah', 'Hag': 'Haggai', 'Zec': 'Zechariah', 'Mal': 'Malachi'
}

# ==========================================
# PARSING LOGIC
# ==========================================

def explode_standard_ref(ref_str):
    """
    Takes a Standard Ref like 'Gen.2:25-3:1' or 'Gen.5:32; 6:1'
    and returns a LIST of atomic refs: ['Gen.2:25', 'Gen.3:1']
    """
    clean_ref = ref_str.split('!')[0]
    atomic_refs = []
    
    # 1. Split disjoint lists (semicolons)
    parts = re.split(r'[;,]\s*', clean_ref)
    
    for part in parts:
        if not part.strip(): continue
        
        # 2. Handle Ranges (Hyphens)
        if '-' in part:
            subparts = part.split('-')
            start = subparts[0]
            end = subparts[1]
            
            # Regex: Book.Chapter:Verse
            base_match = re.match(r'([1-3]?[A-Za-z]+\.\d+:)', start)
            if not base_match:
                atomic_refs.append(start)
                continue
                
            base_prefix = base_match.group(1) # e.g. "Gen.32:"
            
            start_v_match = re.search(r':(\d+)', start)
            end_v_match = re.search(r'(\d+)', end)
            
            # Expand atomic range if it is within same chapter (e.g. 1:1-5)
            if start_v_match and end_v_match and ':' not in end:
                s_num = int(start_v_match.group(1))
                e_num = int(end_v_match.group(1))
                for v in range(s_num, e_num + 1):
                    atomic_refs.append(f"{base_prefix}{v}")
            else:
                # Cross-chapter or complex range: Keep endpoints to ensure coverage
                atomic_refs.append(start)
                if not re.match(r'[1-3]?[A-Za-z]+\.', end):
                     book_code = start.split('.')[0]
                     atomic_refs.append(f"{book_code}.{end}")
                else:
                    atomic_refs.append(end)
        else:
            # Single ref handling
            if not re.match(r'[1-3]?[A-Za-z]+\.', part):
                # Attempt to recover book code from context (previous part)
                if parts[0] != part:
                     prev_book = parts[0].split('.')[0]
                     atomic_refs.append(f"{prev_book}.{part}")
                else:
                     atomic_refs.append(part)
            else:
                atomic_refs.append(part)
                
    return atomic_refs

def parse_dataset(filename):
    data = {}
    data_started = False

    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter='\t')
        
        for row in reader:
            if not data_started:
                if row and "#DataStart(Expanded)" in row[0]:
                    data_started = True
                continue
            
            if not row or row[0].startswith("'") or row[0].startswith("SourceType") or len(row) < 3:
                continue

            source_type = row[0]
            source_ref = row[1]
            std_ref_raw = row[2]

            # UNROLL: Get list of atomic Standard IDs
            std_ids = explode_standard_ref(std_ref_raw)

            for std_ref in std_ids:
                if std_ref not in data:
                    data[std_ref] = {}

                if "Hebrew" in source_type:
                    data[std_ref]['Hebrew'] = source_ref
                elif "Eng-KJV" in source_type and "Latin" not in source_type and "Greek" not in source_type:
                    data[std_ref]['Hebrew'] = source_ref

                if "Latin" in source_type:
                    data[std_ref]['Latin'] = source_ref

                if "Greek" in source_type:
                    data[std_ref]['Greek'] = source_ref
    return data

def clean_ref_output(ref_string, book_map):
    """
    Cleans up internal formatting to User Format.
    Returns (Book, Verse) or (None, None) if invalid/absent.
    """
    if not ref_string or "Absent" in ref_string:
        return "ABSENT", "ABSENT"

    clean = ref_string.split('[')[0].split('!')[0].strip()
    
    match = re.match(r"([1-3]?[A-Za-z]+)\.(\d+:\d+.*)", clean)
    if match:
        book_code = match.group(1)
        verse_part = match.group(2)
        book_name = book_map.get(book_code)
        
        # Return None if book exists in data (like Mat) but not in user map
        if not book_name:
            return None, None
            
        return book_name, verse_part
        
    return "Unknown", clean

def generate_csv(data, output_file):
    print(f"Generating atomic CSV...")
    
    headers = [
        'Standard_ID',
        'JPS_Book', 'JPS_Ref',
        'Vulgate_Book', 'Vulgate_Ref',
        'LXX_Book', 'LXX_Ref'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        sorted_keys = sorted(data.keys()) 
        
        for std_id in sorted_keys:
            traditions = data[std_id]
            
            raw_hebrew = traditions.get('Hebrew', std_id)
            raw_latin = traditions.get('Latin', std_id)
            raw_greek = traditions.get('Greek', std_id)

            # --- JPS Processing ---
            jps_book, jps_vers = clean_ref_output(raw_hebrew, USFM_TO_JPS)
            
            # --- FILTERING ---
            # 1. None: Book not in your JPS list (e.g. NT books)
            # 2. "Unknown": Regex parsing failed
            # 3. "ABSENT": The verse does not exist in JPS
            if jps_book is None or jps_book == "Unknown" or jps_book == "ABSENT":
                continue

            # --- Target Processing ---
            vul_book, vul_vers = clean_ref_output(raw_latin, USFM_TO_VULGATE)
            lxx_book, lxx_vers = clean_ref_output(raw_greek, USFM_TO_LXX)

            writer.writerow([
                std_id,
                jps_book, jps_vers,
                vul_book, vul_vers,
                lxx_book, lxx_vers
            ])

    print(f"Success. File saved to: {output_file}")

if __name__ == "__main__":
    mapped_data = parse_dataset(INPUT_FILENAME)
    generate_csv(mapped_data, OUTPUT_FILENAME)
