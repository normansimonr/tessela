import pandas as pd
import re
import json
import os
import csv

with open("annotation_equivalences_hebrew.json", "r") as file:
    # Parse the JSON data into a dictionary
    annotation_equivalences_hebrew = json.load(file)

with open("annotation_equivalences_greek.json", "r") as file:
    # Parse the JSON data into a dictionary
    annotation_equivalences_greek = json.load(file)

with open("tov_ebible_equivalences.json", "r") as file:
    # Parse the JSON data into a dictionary
    # Structure is "Tov": "EBIBLE"
    tov_ebible_equivalences = json.load(file)

def convert_to_dataframe(file_path):
    """
    This function converts the raw .par files into Pandas DataFrames
    """

    # Open the file for reading
    with open(file_path, "r") as file:
        # Read the contents of the file into a string variable
        parallel_raw = file.read()

    # Correcting wrong input syntax
    parallel_raw = parallel_raw.replace(
        "W/)T H/GRG$Y ^ =W/)T W/H/)MRY KAI\ TO\\N AMORRAI=ON",
        "W/)T H/GRG$Y ^ =W/)T W/H/)MRY 	KAI\ TO\\N AMORRAI=ON",
    )  # JoshB 3:10
    parallel_raw = parallel_raw.replace(
        "W/H/KHNYM =W/H/)BNYM .m .kb # KAI\ OI( LI/QOI ",
        "W/H/KHNYM =W/H/)BNYM .m .kb 	KAI\ OI( LI/QOI ",
    )  # JoshB 4:11
    parallel_raw = parallel_raw.replace(
        "W/YC+YRW =;W/YC+YDW .rd <9.12 E)PESITI/SANTO {d} KAI\ H(TOIMA/SANTO ",
        "W/YC+YRW =;W/YC+YDW .rd <9.12 	E)PESITI/SANTO {d} KAI\ H(TOIMA/SANTO ",
    )  # JoshB 9:4
    parallel_raw = parallel_raw.replace(
        "--+ '' =;L/GBWLWT/YHM <19.49> E)N TOI=S O(RI/OIS AU)TW=N ",
        "--+ '' =;L/GBWLWT/YHM <19.49> 	 E)N TOI=S O(RI/OIS AU)TW=N ",
    )  # JoshB 24:42
    parallel_raw = parallel_raw.replace(
        """E)N TH=| BASILEI/A| \nAU)TOU=""", "E)N TH=| BASILEI/A| AU)TOU="
    )  # 1Chr 4:23
    parallel_raw = parallel_raw.replace(
        """E)NNAKO/SIOI PENTH/KONTA \nE(/C""", "E)NNAKO/SIOI PENTH/KONTA E(/C"
    )  # 1Chr 9:9
    parallel_raw = parallel_raw.replace(
        """TOU= E)PONOMA/SAI TO\ O)/NOMA/ \nMOU""",
        "TOU= E)PONOMA/SAI TO\ O)/NOMA/ \nMOU",
    )  # 1Chr 28:3
    parallel_raw = parallel_raw.replace("""[96.7]\n\nPSL""", "[96.7]\nPSL")  # Psa. 97:7
    parallel_raw = parallel_raw.replace("""[11.2]\n\nPSW""", "[11.2]\nPSW")  # Psa. 12:2
    parallel_raw = parallel_raw.replace(
        """[47.14]\n\nPSGW""", "[47.14]\nPSGW"
    )  # Psa. 48:14
    parallel_raw = parallel_raw.replace(
        """[71.16]\n\nPST""", "[71.16]\nPST"
    )  # Psa. 72:16
    parallel_raw = parallel_raw.replace("""[37c]\n\n--+""", "[37c]\n--+")  # DanOG. 4:34

    parallel_raw = parallel_raw.replace("--=", "--+")  # Genesis 6:19
    parallel_raw = parallel_raw.replace(
        "^^^                                    *", "~~~"
    )  # Deut 28:65
    parallel_raw = parallel_raw.replace("^^^", "~~~").replace(
        "^", ""
    )  # Elsewhere in Deut
    parallel_raw = parallel_raw.replace("''=", "'' =")  # JoshB 24:4
    parallel_raw = parallel_raw.replace(";=L/PNY", "=;L/PNY")  # 1Sam 1:24
    parallel_raw = parallel_raw.replace(";=YHWH", "=;YHWH")  # 1Sam 1:24
    parallel_raw = parallel_raw.replace(":=NX$", "=:NX$")  # 1Sam 11:10
    parallel_raw = parallel_raw.replace(":=H/(MWNY", "=:H/(MWNY")  # 1Sam 11:10
    parallel_raw = parallel_raw.replace(";=W/K/ZHB", "=;W/K/ZHB")  # Mal 3:3
    parallel_raw = parallel_raw.replace(
        "{...?AU)TOU=} MDBR =v	LALOU=NTOS", "MDBR =v	{...?AU)TOU=} LALOU=NTOS"
    )  # Ez 2:2
    parallel_raw = parallel_raw.replace(
        "W/MR$Y(=?W/B/R$(Y .mb	KAI\ E)N A(MARTI/AIS",
        "W/MR$Y( = ?W/B/R$(Y .mb	KAI\ E)N A(MARTI/AIS",
    )  # DanOG 11:32

    parallel_raw = parallel_raw.replace(
        "{...K/}{...)$R}	O(\\N TRO/PON O(/TAN", "{...K/} {...)$R}	O(\\N TRO/PON O(/TAN"
    )  # Zec 4:1 - Not an input error, but program breaks if two curly patterns are in the same word
    parallel_raw = parallel_raw.replace(
        "{...W/}{...)L}	KAI\ MH\\", "{...W/} {...)L}	KAI\ MH\\"
    )  # Jer 7:16 - Not an input error, but program breaks if two curly patterns are in the same word

    # Splits the text into verses or 'paragraphs' (separated in the raw files by empty lines)
    paragraphs = re.split(r"\n\s*\n", parallel_raw.strip())

    # Below code converts the raw text into a Pandas DataFrame
    parallels_dataframe_list = []
    # Loop through the list of paragraphs and extract the first line of each paragraph
    for paragraph in paragraphs:
        # Split the paragraph by newline characters
        lines = paragraph.split("\n")
        if lines:
            first_line = lines[0]
            other_lines = lines[1:]  # Get the lines other than the first line

        parallel = pd.DataFrame(other_lines, columns=["words"])
        parallel["coords"] = first_line
        parallels_dataframe_list.append(parallel)

    parallel = pd.concat(parallels_dataframe_list)
    # parallel.to_csv('aver.csv')
    
    # Splitting the text so that we have the Masoretic and the LXX columns
    parallel[["masoretic", "lxx"]] = parallel["words"].str.split("\t", n=1, expand=True)
    parallel = parallel.drop(columns=["words"])

    # Adding the order by column
    parallel = parallel.reset_index()
    parallel = parallel.drop(columns=["index"])
    parallel = parallel.reset_index()
    parallel = parallel.rename(columns={"index": "orderby"})
    parallel["orderby"] = parallel["orderby"] + 1

    # Splitting the coordinates
    parallel["coords"] = parallel["coords"].str.replace(
        "Obad ", "Obad 1:"
    )  # Obadiah only has one chapter
    parallel[["book", "chapter_verse"]] = parallel["coords"].str.split(" ", expand=True)
    parallel = parallel.drop(columns=["coords"])

    parallel[["chapter", "verse"]] = parallel["chapter_verse"].str.split(
        ":", expand=True
    )
    parallel = parallel.drop(columns=["chapter_verse"])

    # Splitting the masoretic text
    # Replacing = with another separator
    new_separator = "■"

    def replace_equals_as_separator(text):
        dont_replace_if_followed_by = ["%", ";", "+", "@", ":", "v", "r", "p"]

        words = text.split()

        new_words = []
        for word in words:
            if "=" in word:
                if word == "=":
                    new_words.append(new_separator)
                elif word[0] == "=":
                    if word[1] in dont_replace_if_followed_by:
                        new_words.append(word)
                    else:
                        new_words.append(word.replace("=", new_separator))
                elif word[:4] == "--=;":  # Happens in Genesis 22:16 and Exodus 10:24
                    new_words.append(word.replace("--=;", "=; "))
                elif word[:3] == "?=?":  # Happens in Exodus 4:25
                    new_words.append(word.replace("?=?", new_separator + " ? "))
                else:
                    raise ValueError("I don't understand this syntax:", word)
            else:
                new_words.append(word)

        return " ".join(new_words)

    parallel["masoretic"] = parallel["masoretic"].apply(replace_equals_as_separator)

    # Splitting the columns
    parallel[["masoretic", "retroverted"]] = parallel["masoretic"].str.split(
        new_separator, n=1, expand=True
    )
    
    # Reordering the columns
    parallel = parallel[
        ["book", "chapter", "verse", "orderby", "masoretic", "retroverted", "lxx"]
    ]

    # Replacing nulls with empty strings
    parallel = parallel.fillna("")

    # parallel.to_csv('aver.csv')

    return parallel


def protect_annotations(parallel):
    """
    Encloses annotations in !! to prevent them from being converted to Hebrew characters
    """

    def enclose_annotation_word_hebrew(word):
        if word in annotation_equivalences_hebrew.keys():
            return "!" + word + "!"
        else:
            return word

    def enclose_annotation_word_greek(word):
        if word in annotation_equivalences_greek.keys():
            return "!" + word + "!"
        else:
            return word

    # Making some markers standalone so that they can be protected
    make_these_standalone_words = ["?", "=:", "=@"]
    for mark in make_these_standalone_words:
        for column in ["masoretic", "retroverted", "lxx"]:
            parallel[column] = parallel[column].str.replace(
                mark, " " + mark + " ", regex=False
            )

    # Now making the {..} markers standalone too
    def find_and_replace_curly_markers(text):
        patterns = {
            r"\{\.\.p([^}]*)\}": " {..p} ",
            r"\{\.\.d([^}]*)\}": " {..d} ",
            r"\{\.\.r([^}]*)\}": " {..r} ",
            r"\{\.\.\.([^}]*)\}": " {...} ",
            r"\{\.\.\~([^}]*)\}": " {..~} ",
        }

        words = text.split()

        word_list = []
        for word in words:
            matched_patterns = []
            for pattern in patterns.keys():
                matches = re.findall(pattern, word)
                if len(matches) == 1:
                    matched_patterns.append(patterns[pattern] + matches[0])
                elif len(matches) > 1:
                    raise ValueError("Wrong syntax! (too many patterns?)", text)
                else:
                    pass
            if len(matched_patterns) == 1:
                word_list.append(matched_patterns[0])
            elif len(matched_patterns) == 0:
                word_list.append(word)
            else:
                raise ValueError("Wrong syntax! (too many patterns?)", text)
        return " ".join(word_list)

    for column in ["masoretic", "retroverted", "lxx"]:
        parallel[column] = parallel[column].apply(find_and_replace_curly_markers)

    for column in ["masoretic", "retroverted"]:
        parallel[column] = parallel[column].apply(
            lambda x: " ".join(
                [enclose_annotation_word_hebrew(word) for word in x.split()]
            )
        )

    parallel["lxx"] = parallel["lxx"].apply(
        lambda x: " ".join([enclose_annotation_word_greek(word) for word in x.split()])
    )

    # Removing multiple spaces
    for column in ["masoretic", "retroverted", "lxx"]:
        parallel[column] = parallel[column].str.replace(r"\s+", " ", regex=True)

    return parallel


def convert_hebrew_to_unicode(parallel):
    # Open the JSON file for reading
    with open("hebrew_equivalences.json", "r") as file:
        # Parse the JSON data into a dictionary
        hebrew_equivalences = json.load(file)

    # Dictionary of non-final Hebrew letters and their final equivalents
    hebrew_final_equivalences = {
        "כ": "ך",  # Kaf to final Kaf
        "מ": "ם",  # Mem to final Mem
        "נ": "ן",  # Nun to final Nun
        "פ": "ף",  # Pe to final Pe
        "צ": "ץ",  # Tsadi to final Tsadi
    }

    # Function to replace non-final Hebrew letters with their final equivalents
    def replace_final_in_word(word):
        word = word.replace("\u200e", "")
        if word[-1] in hebrew_final_equivalences:
            word = word[:-1] + hebrew_final_equivalences[word[-1]]
        return word

    # Replacing nulls with empty strings
    parallel = parallel.fillna("")

    # Function to replace with Unicode characters, except annotations
    def replace_with_unicode_except_annotations(text):
        words = text.split()

        words_list = []
        for word in words:
            if word.startswith("!") and word.endswith("!"):
                words_list.append(word)
            else:
                word_result = []
                for character in word:
                    word_result.append(hebrew_equivalences.get(character, character))
                words_list.append("".join(word_result))
        return " ".join(words_list)

    # Removing the / character and replacing with the Unicode letters
    for column in ["masoretic", "retroverted"]:
        parallel[column] = parallel[column].str.replace("/", "")
        parallel[column] = parallel[column].apply(
            replace_with_unicode_except_annotations
        )
        parallel[column] = parallel[column].apply(
            lambda x: " ".join([replace_final_in_word(word) for word in x.split()])
        )

    return parallel


def convert_greek_to_unicode(parallel):
    # Open the JSON file for reading
    with open("greek_equivalences.json", "r") as file:
        # Parse the JSON data into a dictionary
        greek_equivalences = json.load(file)

    # Temporarily masking the {*} and {**} symbols
    parallel["lxx"] = parallel["lxx"].str.replace("{*}", "oneasterisk", regex=False)
    parallel["lxx"] = parallel["lxx"].str.replace("{**}", "twoasterisks", regex=False)

    # Removing diacritics
    diacritics = [")", "(", "|", "/", "\\", "=", "+", "*"]

    for diacritic in diacritics:
        parallel["lxx"] = parallel["lxx"].str.replace(diacritic, "", regex=False)

    # Putting back the {*} and {**} symbols
    parallel["lxx"] = parallel["lxx"].str.replace("oneasterisk", "{*}", regex=False)
    parallel["lxx"] = parallel["lxx"].str.replace("twoasterisks", "{**}", regex=False)

    # Replacing the original value for koppa (#3) with a single letter, Ñ
    # This makes it easier to replace with the Greek Unicode
    parallel["lxx"] = parallel["lxx"].str.replace("#3", "Ñ")

    # Replacing code with Unicode
    parallel["lxx"] = parallel["lxx"].apply(
        lambda x: "".join(greek_equivalences.get(c, c) for c in x)
    )

    # Function to replace non-final sigma with its final equivalent
    def replace_final_sigma(word):
        if word[-1] == "σ":
            word = word[:-1] + "ς"
        return word

    parallel["lxx"] = parallel["lxx"].apply(
        lambda x: " ".join([replace_final_sigma(word) for word in x.split()])
    )

    return parallel


def replace_annotations(parallel):

    # Detecting potential differences in Hebrew Vorlage
    selected_markers = ['--- {x}', '--+ {x}', '---', '--+', "''", '{v}', 'G', '=+', '=r', '.']
    
    parallel['potential_difference'] = parallel['masoretic'].apply(lambda x: any('!' + marker + '!' in x for marker in selected_markers)) | parallel['lxx'].apply(lambda x: any('!' + marker + '!' in x for marker in selected_markers))
    
    # Adding a potential difference where there is a retroversion
    parallel['potential_difference'] = parallel['potential_difference'] | parallel['retroverted'].apply(lambda x: x != '')
    
    def replace_these_annotations(text, language):
        words = text.split()

        words_list = []
        for word in words:
            if word.startswith("!") and word.endswith("!"):
                word = word[1:-1]
                if language == "hebrew":
                    words_list.append(
                        "•^[" + annotation_equivalences_hebrew[word] + "]"
                    )
                elif language == "greek":
                    # print(text)
                    words_list.append("•^[" + annotation_equivalences_greek[word] + "]")
            else:
                words_list.append(word)
        return " ".join(words_list)

    for column in ["masoretic", "retroverted"]:
        parallel[column] = parallel[column].apply(
            lambda x: replace_these_annotations(x, "hebrew")
        )

    parallel["lxx"] = parallel["lxx"].apply(
        lambda x: replace_these_annotations(x, "greek")
    )

    return parallel


## Wrapper function


def convert_to_csv_unicode(file_path):
    print("Processing", file_path)
    parallel = convert_to_dataframe(file_path)
    parallel = protect_annotations(parallel)
    parallel = convert_hebrew_to_unicode(parallel)
    parallel = convert_greek_to_unicode(parallel)
    parallel = replace_annotations(parallel)
    return parallel


def run_tov_conversion():
    files_to_convert = [
        ["../../data/raw/LXX_Tov/01.Genesis.par", "Genesis"],
        ["../../data/raw/LXX_Tov/02.Exodus.par", "Exodus"],
        ["../../data/raw/LXX_Tov/03.Lev.par", "Leviticus"],
        ["../../data/raw/LXX_Tov/04.Num.par", "Numbers"],
        ["../../data/raw/LXX_Tov/05.Deut.par", "Deuteronomy"],
        ["../../data/raw/LXX_Tov/06.JoshB.par", "Joshua (Vaticanus)"],
        ["../../data/raw/LXX_Tov/07.JoshA.par", "Joshua (Alexandrinus)"],
        ["../../data/raw/LXX_Tov/08.JudgesB.par", "Judges (Vaticanus)"],
        ["../../data/raw/LXX_Tov/09.JudgesA.par", "Judges (Alexandrinus)"],
        ["../../data/raw/LXX_Tov/10.Ruth.par", "Ruth"],
        ["../../data/raw/LXX_Tov/11.1Sam.par", "1 Samuel"],
        ["../../data/raw/LXX_Tov/12.2Sam.par", "2 Samuel"],
        ["../../data/raw/LXX_Tov/13.1Kings.par", "1 Kings"],
        ["../../data/raw/LXX_Tov/14.2Kings.par", "2 Kings"],
        ["../../data/raw/LXX_Tov/15.1Chron.par", "1 Chronicles"],
        ["../../data/raw/LXX_Tov/16.2Chron.par", "2 Chronicles"],
        ["../../data/raw/LXX_Tov/18.Esther.par", "Esther"],
        ["../../data/raw/LXX_Tov/18.Ezra.par", "Ezra"],
        ["../../data/raw/LXX_Tov/19.Neh.par", "Nehemiah"],
        ["../../data/raw/LXX_Tov/20.Psalms.par", "Psalms"],
        ["../../data/raw/LXX_Tov/23.Prov.par", "Proverbs"],
        ["../../data/raw/LXX_Tov/24.Qoh.par", "Ecclesiastes"],
        ["../../data/raw/LXX_Tov/25.Cant.par", "Song of Songs"],
        ["../../data/raw/LXX_Tov/26.Job.par", "Job"],
        ["../../data/raw/LXX_Tov/28.Hosea.par", "Hosea"],
        ["../../data/raw/LXX_Tov/29.Micah.par", "Micah"],
        ["../../data/raw/LXX_Tov/30.Amos.par", "Amos"],
        ["../../data/raw/LXX_Tov/31.Joel.par", "Joel"],
        ["../../data/raw/LXX_Tov/32.Jonah.par", "Jonah"],
        ["../../data/raw/LXX_Tov/33.Obadiah.par", "Obadiah"],
        ["../../data/raw/LXX_Tov/34.Nahum.par", "Nahum"],
        ["../../data/raw/LXX_Tov/35.Hab.par", "Habakkuk"],
        ["../../data/raw/LXX_Tov/36.Zeph.par", "Zephaniah"],
        ["../../data/raw/LXX_Tov/37.Haggai.par", "Haggai"],
        ["../../data/raw/LXX_Tov/38.Zech.par", "Zechariah"],
        ["../../data/raw/LXX_Tov/39.Malachi.par", "Malachi"],
        ["../../data/raw/LXX_Tov/40.Isaiah.par", "Isaiah"],
        ["../../data/raw/LXX_Tov/41.Jer.par", "Jeremiah"],
        ["../../data/raw/LXX_Tov/43.Lam.par", "Lamentations"],
        ["../../data/raw/LXX_Tov/44.Ezekiel.par", "Ezekiel"],
        ["../../data/raw/LXX_Tov/45.DanielOG.par", "Daniel (Old Greek)"],
        ["../../data/raw/LXX_Tov/46.DanielTh.par", "Daniel (Theodotion)"],
    ]


    all_books_data = []

    print("Processing TOV LXX .par files...")
    for book in files_to_convert:
        processed_df = convert_to_csv_unicode(file_path=book[0])
        # Add book name and chapter to the DataFrame before appending
        processed_df["book_name"] = book[1]
        all_books_data.append(processed_df)

    # Concatenate all DataFrames into a single DataFrame
    final_df = pd.concat(all_books_data, ignore_index=True)

    # Clean up text columns for CSV export
    for col in ["masoretic", "retroverted", "lxx"]:
        # Replace newlines with a space
        final_df[col] = final_df[col].str.replace(r'\n', ' ', regex=True)
        # Replace double quotes with two double quotes (CSV standard for escaping quotes)
        final_df[col] = final_df[col].str.replace('"', '""', regex=False)

    # Replace book IDs with ebible compatible IDs
    
    final_df['book'] = final_df['book'].replace(tov_ebible_equivalences)
    
    # Removing Vaticanus (Joshua and Judges) and Theodotion
    
    final_df = final_df[~final_df['book'].isin(['JoshA', 'JudgA', 'DanTh'])]
    
    
    # Define the output CSV file path
    output_csv_path = "../../data/intermediate_datasets/tov.csv"

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    # Write the final DataFrame to a single CSV file
    final_df.to_csv(output_csv_path, index=False, quoting=csv.QUOTE_ALL)
    print(f"Successfully extracted all data to {output_csv_path}")

if __name__ == "__main__":
    run_tov_conversion()


