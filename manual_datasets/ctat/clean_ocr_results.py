import pandas as pd

df = pd.read_csv("ocr_results.csv")

df = df.drop_duplicates(subset='text', keep='first')

df['text'] = df["text"].str.replace('‘', '')\
    .str.replace('.', ',')\
    .str.replace('~', '')\
    .str.replace('"', '')\
    .str.replace('Fz', 'Ez')\
    .str.replace('Fiz', 'Ez')\
    .str.replace('Bz', 'Ez')\
    .str.replace('pp', 'Ps')\
    .str.replace('J ', 'Jl')\
    .str.replace('Jt', 'Jl')\
    .str.replace('Ir ', 'Jr ')\
    .str.replace('In ', 'Jr ')\
    .str.replace('Jn ', 'Jr ')\
    .str.replace('dr ', 'Jr ')\
    .str.replace('Il Ch', 'II Ch ')\
    .str.replace('I] Ch', 'II Ch ')\
    .str.replace('1] Ch', 'II Ch ')\
    .str.replace('{1 Ch', 'II Ch ')\
    .str.replace('11Ch', 'II Ch')\
    .str.replace('| Ch', 'I Ch')\
    .str.replace('I Ch 20,25B', 'II Ch 20,25B')\
    .str.replace('1$', 'I S')\
    .str.replace('1S', 'I S')\
    .str.replace('1I S', 'II S')\
    .str.replace('11S', 'II S')\
    .str.replace('11 Ch', 'II Ch')\
    .str.replace('1I Ch', 'II Ch')\
    .str.replace('Jg2,1', 'Jg 2,1')\
    .str.replace('Jg5,11', 'Jg 5,11')\
    .str.replace('Jg7,3', 'Jg 7,3')\
    .str.replace('Jg9,31A', 'Jg 9,31')\
    .str.replace('1$1,24A', 'I S 1,24')\
    .str.replace('1$3,13A', 'I S 3,13')\
    .str.replace('1$7,2', 'I S 7,2')\
    .str.replace('1$9,24A', 'I S 9,24')\
    .str.replace('1$14,41', 'I S 14,41')\
    .str.replace('WS ', 'II S ')\
    .str.replace('Il ', 'II ')\
    .str.replace('ILS ', 'II S ')\
    .str.replace('It\'S ', 'II S ')\
    .str.replace('11 R', 'II R')\
    .str.replace('I] R', 'II R')\
    .str.replace('Jp ', 'Jr ')\
    .str.replace('MI ', 'Mal ')\
    .str.replace(r"\(.*?\)", "", regex=True).str.strip()

df['text'] = df["text"].str.replace('II Ch', '2Ch')\
    .str.replace('I Ch', '1Ch')\
    .str.replace('II R', '2R')\
    .str.replace('I R', '1R')\
    .str.replace('II S', '2S')\
    .str.replace('I S', '1S')\
    .str.replace(',', ':')

df = df.drop_duplicates(subset='text', keep='first')

a = df["text"].str.split(" ", n=1, expand=True)
a.columns = ["book", "verses"]
df = pd.concat([df, a], axis=1)
del a

df["verses"] = df["verses"].str.replace(r"[A-Za-z]", "", regex=True)

b = df["verses"].str.split("/", expand=True)
b.columns = ["v1", "v2"]
df = pd.concat([df, b], axis=1)
del b

df = df.drop(columns=["text", "page", "verses"])

df = df.melt(id_vars=["volume", "pagina", "book"])

df = df.dropna(subset=["value"])

df = df.drop(columns=["variable"])

df = df.drop_duplicates(subset=["book", "value"], keep='first')

def remove_hyphen_last(text):
    if text[-1] == "-":
        return text[:-1].strip()
    else:
        return text.strip()

df["value"] = df["value"].apply(remove_hyphen_last)

def add_obadiah_chapter(row):
    if row["book"] == "Ab":
        return "1:" + str(row["value"])
    else:
        return str(row["value"])

df["value"] = df[["book", "value"]].apply(add_obadiah_chapter, axis=1)


df.to_csv("ocr_clean.csv", index=False)

print(df)
