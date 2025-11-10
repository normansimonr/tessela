import pandas as pd
from typing import Dict, Any, Optional

from .config import Config

class DataLoader:
    def __init__(self, data_dir: str = Config.DATA_DIR):
        self.data_dir = data_dir
        self.masoretic_df = self._load_data("masoretic.csv")
        self.septuagint_df = self._load_data("septuagint.csv")
        self.vulgate_df = self._load_data("vulgate.csv")
        self.book_name_map = self._create_book_name_map()

    def _load_data(self, filename: str) -> pd.DataFrame:
        """Loads a CSV file into a Pandas DataFrame."""
        filepath = f"{self.data_dir}/{filename}"
        try:
            df = pd.read_csv(filepath)
            # Ensure consistent column names, assuming 'book_name', 'chapter', 'verse', 'text'
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            return df
        except FileNotFoundError:
            print(f"Warning: {filepath} not found.")
            return pd.DataFrame()

    def _create_book_name_map(self) -> Dict[str, str]:
        """
        Creates a mapping of various book name representations to a standardized form.
        This is a simplified example; a more robust solution would involve a comprehensive
        lookup table or a fuzzy matching algorithm.
        """
        standard_names = set(self.masoretic_df['book_name'].unique()) if not self.masoretic_df.empty else set()
        if not self.septuagint_df.empty:
            standard_names.update(self.septuagint_df['book_name'].unique())
        if not self.vulgate_df.empty:
            standard_names.update(self.vulgate_df['book_name'].unique())

        # For simplicity, let's assume the longest name is the standard, or a predefined list
        # This needs to be much more sophisticated for real-world use.
        # For now, we'll just lowercase and remove spaces for mapping.
        name_map = {}
        for name in standard_names:
            name_map[name.lower().replace(' ', '')] = name

        # Add some common variations manually for demonstration
        name_map['gen'] = 'Genesis'
        name_map['ex'] = 'Exodus'
        name_map['1samuel'] = '1 Samuel'
        name_map['1sm'] = '1 Samuel'
        name_map['2samuel'] = '2 Samuel'
        name_map['2sm'] = '2 Samuel'
        # ... extend with more variations as needed

        return name_map

    def _standardize_book_name(self, book_name: str) -> Optional[str]:
        """Standardizes a book name using the internal map."""
        cleaned_name = book_name.lower().replace(' ', '')
        return self.book_name_map.get(cleaned_name)

    def get_verse(self, book_name: str, chapter: int, verse: int, dataset: str) -> Optional[str]:
        """
        Retrieves the text of a specific verse from a given dataset.
        Handles book name reconciliation.
        """
        df: pd.DataFrame
        if dataset.lower() == "masoretic":
            df = self.masoretic_df
        elif dataset.lower() == "septuagint":
            df = self.septuagint_df
        elif dataset.lower() == "vulgate":
            df = self.vulgate_df
        else:
            return None

        if df.empty:
            return None

        standard_book_name = self._standardize_book_name(book_name)
        if not standard_book_name:
            return None # Book name not recognized

        # Attempt to find the verse using the standardized book name
        # This assumes that once standardized, the book name will match in the DataFrame
        # A more robust solution might iterate through known variations if direct match fails
        result = df[(df['book_name'] == standard_book_name) &
                    (df['chapter'] == chapter) &
                    (df['verse'] == verse)]

        if not result.empty:
            return result['text'].iloc[0]
        return None

    def get_all_unique_verses(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns a dictionary of all unique verses (book, chapter, verse) found across all datasets.
        The keys are standardized book names, and values are dictionaries of chapters and verses.
        """
        all_verses = {}

        def add_verses_from_df(df: pd.DataFrame):
            if df.empty:
                return
            for _, row in df.iterrows():
                book = self._standardize_book_name(row['book_name'])
                if not book:
                    continue
                chapter = row['chapter']
                verse = row['verse']

                if book not in all_verses:
                    all_verses[book] = {}
                if chapter not in all_verses[book]:
                    all_verses[book][chapter] = []
                if verse not in all_verses[book][chapter]:
                    all_verses[book][chapter].append(verse)
                    all_verses[book][chapter].sort() # Keep verses sorted

        add_verses_from_df(self.masoretic_df)
        add_verses_from_df(self.septuagint_df)
        add_verses_from_df(self.vulgate_df)

        # Sort chapters and books for consistent ordering
        sorted_all_verses = {}
        for book in sorted(all_verses.keys()):
            sorted_all_verses[book] = {}
            for chapter in sorted(all_verses[book].keys()):
                sorted_all_verses[book][chapter] = all_verses[book][chapter]

        return sorted_all_verses
