class Status:
    books_converted = 0
    books_processed = 0

    @classmethod
    def process_book(cls, converted: bool):
        cls.books_processed += 1
        if converted:
            cls.books_converted += 1

    @classmethod
    def print_report(cls):
        out = "Processed {} books, converted {} books".format(
            cls.books_processed, cls.books_converted
        )
        print(out)
