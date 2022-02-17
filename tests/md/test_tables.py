from pathlib import Path

import pandas as pd
from mkreports import md


class TestTables:
    def test_non_json_types(self, tmp_path):
        """Test if table with non-JSON types can be created."""
        # create an example table with path objects
        test_table = pd.DataFrame(
            [
                dict(name="test", file=Path("test.md")),
                dict(name="test2", file=Path("test2.md")),
            ]
        )

        # create a table instance
        # here we don't need to call 'to_markdown' as the
        # serialization is done during initialization.
        md.Tabulator(
            test_table,
            store_path=tmp_path,
            javascript_path=tmp_path,
            page_path=tmp_path,
            idstore=md.IDStore(),
        )
