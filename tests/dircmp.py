from filecmp import dircmp
from pathlib import Path
from typing import Sequence


def cmp_dirs_recursive(left_dir: Path, right_dir: Path, ignore: Sequence[Path]) -> bool:
    cmp_dirs = dircmp(left_dir, right_dir, ignore=[str(path) for path in ignore])
    if (
        len(cmp_dirs.left_only) > 0
        or len(cmp_dirs.right_only) > 0
        or len(cmp_dirs.diff_files) > 0
        or len(cmp_dirs.funny_files) > 0
        or len(cmp_dirs.common_funny) > 0
    ):
        return False
    else:
        for subdir in cmp_dirs.common_dirs:
            subdir_ignore = [
                path.relative_to(subdir)
                for path in ignore
                if subdir in [str(x) for x in path.parents]
            ]
            print(f"{subdir}: {subdir_ignore}")
            if not cmp_dirs_recursive(
                left_dir / subdir, right_dir / subdir, ignore=subdir_ignore
            ):
                return False
        return True
