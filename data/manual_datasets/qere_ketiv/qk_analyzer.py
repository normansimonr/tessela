import pandas as pd
import numpy as np

qk = pd.read_csv("OT-QK.tsv", sep="\t", header=None)
columns_to_keep = [0,1,6,4,5]
qk = qk.iloc[:,columns_to_keep]
qk.columns = ["Coordinates", "Qere", "Ketiv", "Strongs Q", "Parsing Q"]

# Splitting the coordinates

qk["Coordinates"] = qk["Coordinates"].str.replace("=Q(K)", "")
book_and_verse = qk["Coordinates"].str.split("#", expand=True)[0]
book_and_verse = book_and_verse.str.replace(r"\([^)]*\)", "", regex=True)
word_series = qk["Coordinates"].str.split("#", expand=True)[1].astype(int)
book = book_and_verse.str.split(".", expand=True)[0]
chapter = book_and_verse.str.split(".", expand=True)[1].astype(int)
verse = book_and_verse.str.split(".", expand=True)[2]

qk["book"] = book
qk["chapter"] = chapter
qk["verse"] = verse
qk["word_index"] = word_series
del qk["Coordinates"]

qk = qk[["book", "chapter", "verse", "word_index", "Qere", "Ketiv", "Strongs Q", "Parsing Q"]]



# Splitting the Ketiv

qk["Strongs K"] = qk["Ketiv"].str.split(expand=False).apply(lambda x: x[-1]).str.split("=").apply(lambda x: x[0])
qk["Parsing K"] = qk["Ketiv"].str.split(expand=False).apply(lambda x: x[-1]).str.split("=").apply(lambda x: x[1])


# Removing extra characters
qk["Strongs K"] = qk["Strongs K"].str.replace("(", "").str.replace("/", " ").str.replace("\\", " ")
qk["Parsing K"] = qk["Parsing K"].str.replace(")", "").str.replace("/", " ").str.replace("\\", " ")

qk["Strongs Q"] = qk["Strongs Q"].str.replace("{", "").str.replace("}", "").str.replace("/", " ").str.replace("\\", " ")
qk["Parsing Q"] = qk["Parsing Q"].str.replace("{", "").str.replace("}", "").str.replace("/", " ").str.replace("\\", " ")

# Removing syntactic waws and hes
# Waw
qk["Strongs K"] = qk["Strongs K"].str.replace("H9001", "").str.replace("H9002", "").str.strip()
qk["Strongs Q"] = qk["Strongs Q"].str.replace("H9001", "").str.replace("H9002", "").str.strip()

qk["Parsing K"] = qk["Parsing K"].str.replace("Hc", "").str.replace("HC", "").str.strip()
qk["Parsing Q"] = qk["Parsing Q"].str.replace("Hc", "").str.replace("HC", "").str.strip()


# He
qk["Strongs K"] = qk["Strongs K"].str.replace("H9009", "").str.strip()
qk["Strongs Q"] = qk["Strongs Q"].str.replace("H9009", "").str.strip()
# We don't remove them from the parsing as they are difficult to remove safely

print(qk)


# Splitting the dataset
without_proper_nouns = qk[~qk["Parsing Q"].str.contains("HNpm", na=False)]

different_lexicon_entry = without_proper_nouns[without_proper_nouns["Strongs Q"] != without_proper_nouns["Strongs K"]]

same_lexicon_entry = without_proper_nouns[without_proper_nouns["Strongs Q"] == without_proper_nouns["Strongs K"]]

same_lexicon_entry_different_parsing = same_lexicon_entry[same_lexicon_entry["Parsing Q"] != same_lexicon_entry["Parsing K"]]

same_lexicon_entry_same_parsing = same_lexicon_entry[same_lexicon_entry["Parsing Q"] == same_lexicon_entry["Parsing K"]]

# Saving datasets of interest

different_lexicon_entry.to_csv("different_lexicon_entry.csv", index=False)
same_lexicon_entry_different_parsing.to_csv("same_lexicon_entry_different_parsing.csv", index=False)

# Saving some statistics

stats = [len(qk), len(qk)-len(without_proper_nouns), len(same_lexicon_entry_same_parsing), len(same_lexicon_entry_different_parsing), len(different_lexicon_entry)]
stats = pd.DataFrame(stats).T
stats.columns = ["Words with QK", "Words that are proper nouns", "Words with same lexicon entry and same parsing", "Words with same lexicon entry but different parsing", "Words with different lexicon entry"]
stats.to_csv("stats.csv", index=False)
print(stats.T)
