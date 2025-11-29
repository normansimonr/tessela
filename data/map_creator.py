import csv
import re
import sys

# ==========================================
# BOOK NAME MAPPINGS
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

# Standard Book Order for Sorting (USFM)
USFM_ORDER = [
    'Gen', 'Exo', 'Lev', 'Num', 'Deu', 'Jos', 'Jdg', 'Rut', 
    '1Sa', '2Sa', '1Ki', '2Ki', '1Ch', '2Ch', 'Ezr', 'Neh', 'Est',
    'Job', 'Psa', 'Pro', 'Ecc', 'Sng', 'Isa', 'Jer', 'Lam', 'Ezk', 
    'Dan', 'Hos', 'Jol', 'Amo', 'Oba', 'Jon', 'Mic', 'Nah', 'Hab', 
    'Zep', 'Hag', 'Zec', 'Mal'
]
BOOK_INDICES = {bk: i for i, bk in enumerate(USFM_ORDER)}

# ==========================================
# PARSING UTILITIES
# ==========================================

def parse_single_ref(ref_str, default_book=None, default_chapter=None):
    """
    Parses 'Book.Ch:V', 'Ch:V', or 'V' into a dict {book, chapter, verse}.
    """
    ref_str = ref_str.strip()
    
    # 1. Full Format: Book.Chapter:Verse (e.g. Gen.1:1)
    match = re.match(r"^([^\.]+)\.(\d+|Title):(.+)$", ref_str)
    if match:
        return {'book': match.group(1), 'chapter': match.group(2), 'verse': match.group(3)}

    # 2. Short Format: Chapter:Verse (e.g. 1:1)
    match = re.match(r"^(\d+):(.+)$", ref_str)
    if match:
        return {'book': default_book, 'chapter': match.group(1), 'verse': match.group(2)}

    # 3. Verse Only (e.g. 1 or 1a)
    return {'book': default_book, 'chapter': default_chapter, 'verse': ref_str}

def expand_ref_range(ref_str, last_book_context=None):
    """
    Expands a reference string (semicolons, ranges) into a list of atomic reference dicts.
    E.g. "Jos.4:23-24" -> [{'book':'Jos', 'ch':'4', 'v':'23'}, {'book':'Jos', 'ch':'4', 'v':'24'}]
    """
    if not ref_str: return []
    
    # Handle semicolon lists "Gen.5:32; 6:1"
    if ';' in ref_str:
        atoms = []
        parts = ref_str.split(';')
        ctx_book = last_book_context
        for p in parts:
            sub_atoms = expand_ref_range(p, ctx_book)
            if sub_atoms:
                atoms.extend(sub_atoms)
                ctx_book = sub_atoms[-1]['book']
        return atoms

    # Handle Ranges "Gen.5:31-32" or "23-24"
    if '-' in ref_str:
        parts = ref_str.split('-')
        start_str, end_str = parts[0].strip(), parts[1].strip()
        
        start = parse_single_ref(start_str, default_book=last_book_context)
        # End ref inherits from Start ref
        end = parse_single_ref(end_str, default_book=start['book'], default_chapter=start['chapter'])
        
        results = []
        
        # Range expansion logic
        # Only unfold if book and chapter are the same
        if start['book'] == end['book'] and start['chapter'] == end['chapter']:
            try:
                # Try to expand integers
                s_v_match = re.search(r"(\d+)", start['verse'])
                e_v_match = re.search(r"(\d+)", end['verse'])
                
                if s_v_match and e_v_match:
                    s_v = int(s_v_match.group(1))
                    e_v = int(e_v_match.group(1))
                    if e_v >= s_v:
                        for v in range(s_v, e_v + 1):
                            results.append({'book': start['book'], 'chapter': start['chapter'], 'verse': str(v)})
                    else:
                        results.append(start)
                else:
                    # Non-integer verses, just return endpoints
                    results.append(start)
                    if start['verse'] != end['verse']:
                        results.append(end)
            except:
                results.append(start)
                results.append(end)
        else:
            # Cross-chapter/book: Return endpoints only (cannot fill gap reliably)
            results.append(start)
            results.append(end)
        return results

    # Single Ref
    return [parse_single_ref(ref_str, default_book=last_book_context)]

def get_sort_key(ref):
    """Helper to sort rows by standard reference book order."""
    bk_idx = BOOK_INDICES.get(ref['book'], 999)
    try:
        ch_num = int(ref['chapter']) if ref['chapter'] and ref['chapter'].isdigit() else 0
    except: ch_num = 0
    
    # Verse sorting
    v_str = str(ref['verse'])
    if v_str == 'Title':
        v_num = 0
    else:
        v_match = re.search(r"(\d+)", v_str)
        v_num = int(v_match.group(1)) if v_match else 0
        
    return (bk_idx, ch_num, v_num, v_str)

# ==========================================
# MAIN PROCESS
# ==========================================

def process_file(input_file, output_file):
    print(f"Reading {input_file}...")
    
    # Data Aggregation
    # Key: (StandardBook, StandardChapter, StandardVerse)
    # Value: Dict with keys 'std', 'JPS', 'LXX', 'Vulgate'
    # The values for traditions are now LISTS/SETS of verses to handle 1-to-many
    aggregated_rows = {}
    
    data_section_started = False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            
            # Documentation skipping logic
            if not data_section_started:
                if line.startswith("SourceType"):
                    data_section_started = True
                    continue 
                elif line.startswith("#DataStart"):
                    continue
                else:
                    continue 
            
            if not line or line.startswith('#') or line.startswith("'") or line.startswith("="):
                continue
            
            cols = line.split('\t')
            if len(cols) < 3: continue
            
            source_types_raw = cols[0]
            source_ref_raw = cols[1]
            std_ref_raw = cols[2]
            
            # Filter for specific traditions
            types = [t.strip() for t in source_types_raw.split('+')]
            categories = {} 
            for t in types:
                if 'Hebrew' in t: categories['JPS'] = t
                elif 'Latin' in t: categories['Vulgate'] = t
                elif 'Greek' in t: categories['LXX'] = t
            
            if not categories: continue # Skip if no relevant tradition
            
            # 1. Expand Standard Refs (Rows)
            std_refs = expand_ref_range(std_ref_raw)
            if not std_refs: continue
            
            # 2. Expand Source Refs (Values)
            # Use the first standard ref as the default context for the source
            # (e.g. if Source is just "23-24", it implies the book/chap of the Std ref)
            src_ctx_book = std_refs[0]['book']
            src_refs = expand_ref_range(source_ref_raw, last_book_context=src_ctx_book)
            
            # 3. Pivot Data
            for std in std_refs:
                key = (std['book'], std['chapter'], std['verse'])
                
                if key not in aggregated_rows:
                    aggregated_rows[key] = {
                        'std': std, 
                        'JPS': [], 
                        'LXX': [], 
                        'Vulgate': []
                    }
                
                # Assign expanded source verses to the appropriate tradition lists
                for cat_key in categories.keys():
                    for src in src_refs:
                        # Translate Book Name
                        usfm_book = src['book']
                        trans_book = usfm_book
                        if cat_key == 'JPS':
                            trans_book = USFM_TO_JPS.get(usfm_book, usfm_book)
                        elif cat_key == 'LXX':
                            trans_book = USFM_TO_LXX.get(usfm_book, usfm_book)
                        elif cat_key == 'Vulgate':
                            trans_book = USFM_TO_VULGATE.get(usfm_book, usfm_book)
                        
                        src_data = {
                            'book': trans_book,
                            'chapter': src['chapter'],
                            'verse': src['verse']
                        }
                        
                        # Add to list if not already present (avoid duplicates from overlapping source lines)
                        if src_data not in aggregated_rows[key][cat_key]:
                            aggregated_rows[key][cat_key].append(src_data)

    # 4. Flatten and Unfold to Rows
    final_rows = []
    
    # Sort keys for processing
    sorted_keys = sorted(aggregated_rows.keys(), key=lambda k: get_sort_key(aggregated_rows[k]['std']))
    
    for key in sorted_keys:
        data = aggregated_rows[key]
        std = data['std']
        
        jps_list = data['JPS']
        lxx_list = data['LXX']
        vul_list = data['Vulgate']
        
        # Determine how many rows this Standard Verse expands to.
        # This is the max length of the source mappings.
        # usually 1, but if Vulgate has 2 verses (23, 24) for this std verse, we make 2 rows.
        max_len = max(len(jps_list), len(lxx_list), len(vul_list), 1)
        
        for i in range(max_len):
            # Helper to get item at index i, or repeat last item, or empty?
            # Standard mapping practice for splitting ranges: 
            # If Std maps to Src 23, 24 -> Row 1 has 23, Row 2 has 24.
            # If another column has only 1 item (e.g. JPS 23), should it repeat? 
            # Yes, because JPS 23 aligns with the whole chunk of Vulgate 23-24.
            
            def get_cell(lst, idx):
                if not lst: return ['', '', '']
                # If list has items, but fewer than max_len, repeat the last item (or wrap?)
                # Contextually, repeating the single mapping is safest for alignment.
                if idx >= len(lst):
                    d = lst[-1] # Repeat last known mapping
                else:
                    d = lst[idx]
                return [d['book'], d['chapter'], d['verse']]

            jps_vals = get_cell(jps_list, i)
            lxx_vals = get_cell(lxx_list, i)
            vul_vals = get_cell(vul_list, i)
            
            final_rows.append([
                std['book'], std['chapter'], std['verse'],
                *jps_vals,
                *lxx_vals,
                *vul_vals
            ])

    # 5. Write to CSV
    headers = [
        'Standard_Book', 'Standard_Chapter', 'Standard_Verse',
        'JPS_Book', 'JPS_Chapter', 'JPS_Verse',
        'LXX_Book', 'LXX_Chapter', 'LXX_Verse',
        'Vulgate_Book', 'Vulgate_Chapter', 'Vulgate_Verse'
    ]
    
    print(f"Writing {len(final_rows)} atomic rows to {output_file}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(final_rows)
            
    print("Processing complete.")

if __name__ == "__main__":
    input_filename = "TVTMS - Translators Versification Traditions with Methodology for Standardisation for Eng+Heb+Lat+Grk+Others - STEPBible.org CC BY.txt"
    output_filename = "bible_versification_mapping_atomic.csv"
    
    process_file(input_filename, output_filename)
