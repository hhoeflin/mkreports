import io
from contextlib import redirect_stdout
from filecmp import dircmp
from pathlib import Path


class DirCmp:
    def __init__(
        self, test_output_dir: Path, gold_output_dir: Path, replace_gold: bool
    ) -> None:
        gold_output_dir.mkdir(parents=True, exist_ok=True)
        if replace_gold:
            # this assumes that you delete the gold directory
            # per hand as necessary
            self.test_output_dir = gold_output_dir
        else:
            self.test_output_dir = test_output_dir
        self.gold_output_dir = gold_output_dir

    @property
    def is_same(self) -> bool:
        cmp_dirs = dircmp(self.test_output_dir, self.gold_output_dir)

        if (
            len(cmp_dirs.left_only) > 0
            or len(cmp_dirs.right_only) > 0
            or len(cmp_dirs.funny_files) > 0
            or len(cmp_dirs.common_funny) > 0
        ):
            return False
        else:
            return True

    def report_full_closure(self):
        cmp_dirs = dircmp(self.test_output_dir, self.gold_output_dir)
        s = io.StringIO()
        with redirect_stdout(s):
            cmp_dirs.report_full_closure()

        return s.getvalue()
