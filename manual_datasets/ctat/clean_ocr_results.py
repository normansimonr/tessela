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


df = df.drop_duplicates(subset='text', keep='first')

df.to_csv("ocr_clean.csv", index=False)

print(df)
