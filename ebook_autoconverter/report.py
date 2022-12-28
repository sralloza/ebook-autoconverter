"""Reports module."""


class Report:
    """Handles the information during execution to make a report at the end."""

    books_total = 0
    books_converted = 0

    @classmethod
    def print_report(cls):
        """Prints the report."""
        out = f"Stored {cls.books_total} books, converted {cls.books_converted} books"
        print(out)
