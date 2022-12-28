import shutil
from pathlib import Path

TEST_FOLDER = Path(__file__).parent.resolve().absolute()


def metadata():
    origin = TEST_FOLDER / "data" / "metadata.db"
    destination = TEST_FOLDER / "data" / "books" / "metadata.db"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(origin, destination)


def app():
    origin = TEST_FOLDER / "data" / "app.db"
    destination = TEST_FOLDER / "data" / "config" / "app.db"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(origin, destination)


def main():
    metadata()
    app()


if __name__ == "__main__":
    main()
