import unittest
import pandas as pd
import os

# This import will fail until we create the file in the next step
from src.data_loader import load_data, filter_septuagint

class TestDataLoader(unittest.TestCase):

    def setUp(self):
        """Set up a dummy CSV file for testing."""
        self.dummy_csv_path = 'tests/dummy_data.csv'
        self.septuagint_csv_path = 'tests/dummy_septuagint.csv'
        
        dummy_data = {
            'book_name': ['Genesis', 'Exodus'],
            'chapter': [1, 20],
            'verse': [1, 2],
            'text': ['In the beginning...', 'Thou shalt not...']
        }
        pd.DataFrame(dummy_data).to_csv(self.dummy_csv_path, index=False)

        septuagint_data = {
            'book_name': ['Genesis', 'Genesis', 'Exodus'],
            'chapter': [1, 1, 20],
            'verse': [1, 2, 1],
            'potential_difference_verse': [True, False, True],
            'text': ['Verse 1 text', 'Verse 2 text', 'Verse 3 text']
        }
        pd.DataFrame(septuagint_data).to_csv(self.septuagint_csv_path, index=False)

    def tearDown(self):
        """Remove the dummy CSV file after tests."""
        if os.path.exists(self.dummy_csv_path):
            os.remove(self.dummy_csv_path)
        if os.path.exists(self.septuagint_csv_path):
            os.remove(self.septuagint_csv_path)

    def test_load_data_success(self):
        """Test that data is loaded correctly from a CSV file."""
        df = load_data(self.dummy_csv_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertListEqual(list(df.columns), ['book_name', 'chapter', 'verse', 'text'])

    def test_load_data_file_not_found(self):
        """Test that FileNotFoundError is raised for a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_data('non_existent_file.csv')

    def test_filter_septuagint(self):
        """Test the filtering logic for the Septuagint DataFrame."""
        df = pd.read_csv(self.septuagint_csv_path)
        filtered_df = filter_septuagint(df)
        self.assertEqual(len(filtered_df), 2)
        # Check that only rows with potential_difference_verse == True remain
        self.assertTrue(all(filtered_df['potential_difference_verse']))

if __name__ == '__main__':
    unittest.main()
