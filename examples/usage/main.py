from pathlib import Path

from mkreports import Report
from tables import use_tables

from images import use_images

if __name__ == "__main__":
    report = Report(Path("usage"), site_name="Mkreports documentations")
    # documentation for images
    use_images(report)
    # documentation for tables
    use_tables(report)
