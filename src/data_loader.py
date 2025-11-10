import pandas as pd

def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads data from a CSV file into a pandas DataFrame.

    Args:
        file_path: The path to the CSV file.

    Returns:
        A pandas DataFrame containing the data from the CSV file.
    
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return pd.read_csv(file_path)

def filter_septuagint(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the Septuagint DataFrame to include only verses marked for potential difference.

    Args:
        df: The Septuagint DataFrame.

    Returns:
        A filtered pandas DataFrame.
    """
    if 'potential_difference_verse' not in df.columns:
        # If the column doesn't exist, return the original dataframe
        return df
        
    # The values might be read as strings, so handle 'True' and 'False' strings
    if pd.api.types.is_string_dtype(df['potential_difference_verse']):
        return df[df['potential_difference_verse'].str.lower() == 'true'].copy()
    
    # Handle boolean values
    return df[df['potential_difference_verse'] == True].copy()
