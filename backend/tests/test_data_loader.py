import pytest
import pandas as pd
from unittest.mock import patch, mock_open
from backend.src.data_loader import DataLoader

# Mock data for testing
MOCK_MASORETIC_CSV = """book_name,chapter,verse,text
Genesis,1,1,"In the beginning God created the heaven and the earth."
Genesis,1,2,"And the earth was without form, and void; and darkness was upon the face of the deep."
Exodus,1,1,"Now these are the names of the children of Israel, which came into Egypt; every man and his household came with Jacob."
"""

MOCK_SEPTUAGINT_CSV = """book_name,chapter,verse,text
Gen,1,1,"In the beginning God made the heaven and the earth."
Gen,1,2,"But the earth was unsightly and unfurnished, and darkness was over the abyss."
Leviticus,1,1,"And the Lord called Moses, and spoke to him out of the tabernacle of witness, saying,"
"""

MOCK_VULGATE_CSV = """book_name,chapter,verse,text
Genesis,1,1,"In principio creavit Deus caelum et terram."
Genesis,1,2,"Terra autem erat inanis et vacua, et tenebrae super faciem abyssi: et spiritus Dei ferebatur super aquas."
Numbers,1,1,"Locutusque est Dominus ad Moysen in deserto Sinai, in tabernaculo foederis, prima die mensis secundi, anno altero egressionis eorum de terra Aegypti, dicens:"
"""

@pytest.fixture
def mock_data_files():
    with patch("builtins.open", new_callable=mock_open) as mocked_file_open:
        # Configure mock_open to return different content based on the filename
        def mock_read(filename, mode='r', encoding=None, errors=None, newline=''):
            if "masoretic.csv" in filename:
                mocked_file_open.return_value.__enter__.return_value.read.return_value = MOCK_MASORETIC_CSV
            elif "septuagint.csv" in filename:
                mocked_file_open.return_value.__enter__.return_value.read.return_value = MOCK_SEPTUAGINT_CSV
            elif "vulgate.csv" in filename:
                mocked_file_open.return_value.__enter__.return_value.read.return_value = MOCK_VULGATE_CSV
            else:
                raise FileNotFoundError(f"No mock data for {filename}")
            return mocked_file_open.return_value
        
        mocked_file_open.side_effect = mock_read
        yield mocked_file_open

def test_data_loader_loads_data(mock_data_files):
    loader = DataLoader(data_dir="data") # data_dir is mocked, so actual path doesn't matter
    assert not loader.masoretic_df.empty
    assert not loader.septuagint_df.empty
    assert not loader.vulgate_df.empty
    assert "book_name" in loader.masoretic_df.columns
    assert "text" in loader.masoretic_df.columns

def test_data_loader_handles_missing_file():
    with patch("builtins.open", side_effect=FileNotFoundError):
        loader = DataLoader(data_dir="nonexistent_data")
        assert loader.masoretic_df.empty
        assert loader.septuagint_df.empty
        assert loader.vulgate_df.empty

def test_standardize_book_name():
    loader = DataLoader(data_dir="data") # data_dir is mocked
    # Test some manual mappings
    assert loader._standardize_book_name("gen") == "Genesis"
    assert loader._standardize_book_name("1 Samuel") == "1 Samuel"
    assert loader._standardize_book_name("1samuel") == "1 Samuel"
    assert loader._standardize_book_name("unknown") is None

def test_get_verse(mock_data_files):
    loader = DataLoader(data_dir="data")

    # Test Masoretic
    verse_text = loader.get_verse("Genesis", 1, 1, "masoretic")
    assert verse_text == "In the beginning God created the heaven and the earth."

    # Test Septuagint with different book name
    verse_text = loader.get_verse("Gen", 1, 1, "septuagint")
    assert verse_text == "In the beginning God made the heaven and the earth."

    # Test Vulgate
    verse_text = loader.get_verse("Genesis", 1, 1, "vulgate")
    assert verse_text == "In principio creavit Deus caelum et terram."

    # Test non-existent verse
    verse_text = loader.get_verse("Genesis", 99, 99, "masoretic")
    assert verse_text is None

    # Test non-existent dataset
    verse_text = loader.get_verse("Genesis", 1, 1, "nonexistent")
    assert verse_text is None

def test_get_all_unique_verses(mock_data_files):
    loader = DataLoader(data_dir="data")
    unique_verses = loader.get_all_unique_verses()

    assert "Genesis" in unique_verses
    assert 1 in unique_verses["Genesis"]
    assert 1 in unique_verses["Genesis"][1]
    assert 2 in unique_verses["Genesis"][1]

    assert "Exodus" in unique_verses
    assert 1 in unique_verses["Exodus"]
    assert 1 in unique_verses["Exodus"][1]

    assert "Leviticus" in unique_verses
    assert 1 in unique_verses["Leviticus"]
    assert 1 in unique_verses["Leviticus"][1]

    assert "Numbers" in unique_verses
    assert 1 in unique_verses["Numbers"]
    assert 1 in unique_verses["Numbers"][1]

    # Ensure sorting
    assert list(unique_verses.keys()) == ["Exodus", "Genesis", "Leviticus", "Numbers"]
    assert list(unique_verses["Genesis"].keys()) == [1]
    assert unique_verses["Genesis"][1] == [1, 2]
