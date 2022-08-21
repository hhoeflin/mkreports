from pathlib import Path

import pandas as pd
from mkreports import md


class TestTables:
    def test_non_json_types(self, page_fixtures):
        """Test if table with non-JSON types can be created."""
        # create an example table with path objects
        test_table = pd.DataFrame(
            [
                dict(name="test", file=Path("test.md")),
                dict(name="test2", file=Path("test2.md")),
            ]
        )

        # create a table instance
        md.Tabulator(
            test_table,
        ).render(**page_fixtures)
