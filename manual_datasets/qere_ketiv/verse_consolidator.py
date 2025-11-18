import pandas as pd

same_entry = pd.read_csv("same_lexicon_entry_different_parsing.csv")
same_entry["type"] = "k"

different_entry = pd.read_csv("different_lexicon_entry.csv")
different_entry["type"] = "K"

df = pd.concat([same_entry, different_entry])

df = df.drop_duplicates(subset = ["book", "chapter", "verse", "type"])

df = df.groupby(["book", "chapter", "verse"])["type"].apply(lambda x: ''.join(x)).reset_index()

df.to_csv("qere_ketiv_verses.csv", index=False)

print(df)
