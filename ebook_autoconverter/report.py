"""Reports module."""


class Report:
    """Handles the information during execution to make a report at the end."""

    books_converted = 0
    books_processed = 0

    @classmethod
    def process_book(cls, converted: bool):
        """Reports a book being processed.

        Args:
            converted (bool): if the processed book was converted or not.
        """
        cls.books_processed += 1
        if converted:
            cls.books_converted += 1

    @classmethod
    def print_report(cls):
        """Prints the report."""
        out = f"Processed {cls.books_processed} books, converted {cls.books_converted} books"
        print(out)
