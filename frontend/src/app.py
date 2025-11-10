import streamlit as st
import requests
from typing import Dict, Any, List, Optional

st.set_page_config(layout="wide")

st.title("Biblical Verse Normalizer")

st.write("Select a verse to view its normalized text from different datasets.")

# Backend API URL (assuming it's running locally on port 8000)
BACKEND_URL = "http://localhost:8001"

@st.cache_data
def get_all_unique_verses():
    try:
        response = requests.get(f"{BACKEND_URL}/verses")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend API. Please ensure the backend is running.")
        return {}
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching verses from backend: {e}")
        return {}

unique_verses = get_all_unique_verses()

selected_book: Optional[str] = None
selected_chapter: Optional[int] = None
selected_verse: Optional[int] = None

if unique_verses:
    # Create a flattened list of verses for the dropdown
    # Format: "Book Chapter:Verse"
    verse_options = []
    for book, chapters in unique_verses.items():
        for chapter, verses in chapters.items():
            for verse in verses:
                verse_options.append(f"{book} {chapter}:{verse}")
    
    selected_verse_str = st.selectbox(
        "Select a Verse",
        options=verse_options,
        index=0 # Default to the first verse
    )

    if selected_verse_str:
        # Parse the selected verse string back into book, chapter, verse
        try:
            parts = selected_verse_str.split(" ")
            book_name_parts = []
            chapter_str = ""
            for part in parts:
                if ":" in part:
                    chapter_str = part
                    break
                book_name_parts.append(part)
            
            selected_book = " ".join(book_name_parts)
            selected_chapter = int(chapter_str.split(":")[0])
            selected_verse = int(chapter_str.split(":")[1])
            
            st.write(f"Selected: {selected_book} {selected_chapter}:{selected_verse}")

            # Call backend for normalization
            if selected_book and selected_chapter is not None and selected_verse is not None:
                try:
                    normalization_payload = {
                        "book": selected_book,
                        "chapter": selected_chapter,
                        "verse": selected_verse
                    }
                    response = requests.post(f"{BACKEND_URL}/normalize", json=normalization_payload)
                    response.raise_for_status()
                    normalized_data = response.json()

                    st.session_state.masoretic_output = normalized_data.get("masoretic", "N/A")
                    st.session_state.septuagint_output = normalized_data.get("septuagint", "N/A")
                    st.session_state.vulgate_output = normalized_data.get("vulgate", "N/A")

                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend API for normalization. Please ensure the backend is running.")
                    st.session_state.masoretic_output = "Error: Backend not reachable"
                    st.session_state.septuagint_output = "Error: Backend not reachable"
                    st.session_state.vulgate_output = "Error: Backend not reachable"
                except requests.exceptions.RequestException as e:
                    st.error(f"Error normalizing verse: {e}")
                    st.session_state.masoretic_output = f"Error: {e}"
                    st.session_state.septuagint_output = f"Error: {e}"
                    st.session_state.vulgate_output = f"Error: {e}"
            else:
                st.session_state.masoretic_output = ""
                st.session_state.septuagint_output = ""
                st.session_state.vulgate_output = ""

        except Exception as e:
            st.error(f"Error parsing selected verse: {e}")
            st.session_state.masoretic_output = ""
            st.session_state.septuagint_output = ""
            st.session_state.vulgate_output = ""
    else:
        st.warning("No verses available. Please ensure data files are present and the backend is running correctly.")
        st.session_state.masoretic_output = ""
        st.session_state.septuagint_output = ""
        st.session_state.vulgate_output = ""
else:
    st.warning("No verses available. Please ensure data files are present and the backend is running correctly.")
    st.session_state.masoretic_output = ""
    st.session_state.septuagint_output = ""
    st.session_state.vulgate_output = ""


# Display normalized text
st.subheader("Normalized Verses")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Masoretic")
    st.text_area("Masoretic Text", value=st.session_state.get("masoretic_output", ""), height=200, key="masoretic_output_display")

with col2:
    st.markdown("### Septuagint")
    st.text_area("Septuagint Text", value=st.session_state.get("septuagint_output", ""), height=200, key="septuagint_output_display")

with col3:
    st.markdown("### Vulgate")
    st.text_area("Vulgate Text", value=st.session_state.get("vulgate_output", ""), height=200, key="vulgate_output_display")