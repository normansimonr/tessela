# Data Model: Graphical Verse Normalizer

## Entities

### Verse

-   **Description**: Represents a single biblical verse.
-   **Attributes**:
    -   `book`: The name of the book (e.g., "Genesis").
    -   `chapter`: The chapter number.
    -   `verse`: The verse number.
    -   `text`: The text of the verse.
    -   `dataset`: The source dataset (e.g., "Masoretic", "Vulgate", "Septuagint").

### NormalizationRequest

-   **Description**: Represents a request to normalize a verse.
-   **Attributes**:
        -   `book`: The name of the book.
        -   `chapter`: The chapter number.
        -   `verse`: The verse number.

### NormalizationResponse

-   **Description**: Represents the normalized text of a verse from the three datasets.
-   **Attributes**:
    -   `masoretic`: The normalized text from the Masoretic dataset.
    -   `vulgate`: The normalized text from the Vulgate dataset.
    -   `septuagint`: The normalized text from the Septuagint dataset.
