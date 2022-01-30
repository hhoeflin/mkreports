import io
from contextlib import redirect_stdout
from filecmp import dircmp
from pathlib import Path


def recursive_cmp_dirs_equal(cmp_dirs) -> bool:

    if (
        len(cmp_dirs.left_only) > 0
        or len(cmp_dirs.right_only) > 0
        or len(cmp_dirs.diff_files) > 0
        or len(cmp_dirs.funny_files) > 0
        or len(cmp_dirs.common_funny) > 0
    ):
        return False
    else:
        # recurse into common subdirectories
        for cmp_subdirs in cmp_dirs.subdirs.values():
            if not recursive_cmp_dirs_equal(cmp_subdirs):
                return False
        return True


class DirCmp:
    def __init__(self, test_output_dir: Path, gold_output_dir: Path) -> None:
        self.test_output_dir = test_output_dir
        self.gold_output_dir = gold_output_dir

    @property
    def is_same(self) -> bool:
        return recursive_cmp_dirs_equal(
            dircmp(self.test_output_dir, self.gold_output_dir)
        )

    def report_full_closure(self):
        cmp_dirs = dircmp(self.test_output_dir, self.gold_output_dir)
        s = io.StringIO()
        with redirect_stdout(s):
            cmp_dirs.report_full_closure()

        return s.getvalue()
