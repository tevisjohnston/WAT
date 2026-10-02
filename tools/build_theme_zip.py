#!/usr/bin/env python3
"""Build the buyer-facing affiliate-theme.zip from the committed wp-dfy theme.

The zip holds exactly what `git archive HEAD` has for the theme directory,
under a single top-level `affiliate-theme/` folder (what WordPress's
Upload Theme screen expects), minus the developer-only CLAUDE.md.

Usage:
    .venv/bin/python tools/build_theme_zip.py [--out deliverables/affiliate-theme.zip]
"""

import argparse
import io
import re
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path("/home/tevis/wp-dfy")
THEME_PATH = "wp-content/themes/affiliate-theme"
PREFIX = "affiliate-theme/"
EXCLUDE = {"CLAUDE.md"}
WAT = Path(__file__).resolve().parent.parent


def git(*args: str, binary: bool = False):
    result = subprocess.run(
        ["git", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
    )
    return result.stdout if binary else result.stdout.decode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=str(WAT / "deliverables" / "affiliate-theme.zip"))
    args = parser.parse_args()
    out = Path(args.out)

    dirty = git("status", "--porcelain", "--", THEME_PATH).strip()
    if dirty:
        print("ERROR: the theme has uncommitted changes; commit them first:\n" + dirty, file=sys.stderr)
        return 1

    archive = git("archive", "--format=zip", f"HEAD:{THEME_PATH}", binary=True)
    # git archive writes MS-DOS entries with no Unix mode, which unzip on a Mac
    # turns into 000 folders and 600 files. Take each file's mode from git.
    executable = {
        line.split("\t", 1)[1]
        for line in git("ls-tree", "-r", f"HEAD:{THEME_PATH}").splitlines()
        if line.startswith("100755 ")
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    names = []
    with zipfile.ZipFile(io.BytesIO(archive)) as src, zipfile.ZipFile(
        out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as dst:
        for info in src.infolist():
            if info.filename in EXCLUDE:
                continue
            data = b"" if info.is_dir() else src.read(info)
            new = zipfile.ZipInfo(PREFIX + info.filename, date_time=info.date_time)
            new.create_system = 3
            if info.is_dir():
                new.external_attr = (0o40755 << 16) | 0x10
            elif info.filename in executable:
                new.external_attr = 0o100755 << 16
            else:
                new.external_attr = 0o100644 << 16
            new.compress_type = zipfile.ZIP_STORED if info.is_dir() else zipfile.ZIP_DEFLATED
            dst.writestr(new, data)
            if not info.is_dir():
                names.append(info.filename)

    style = git("show", f"HEAD:{THEME_PATH}/style.css")
    version = re.search(r"^Version:\s*(\S+)", style, re.M)
    commit = git("rev-parse", "--short", "HEAD").strip()

    if "style.css" not in names:
        print("ERROR: style.css missing from the archive", file=sys.stderr)
        return 1

    size = out.stat().st_size
    print(f"wrote {out}")
    print(f"  theme version {version.group(1) if version else '?'} (wp-dfy {commit})")
    print(f"  {len(names)} files, {size / 1024 / 1024:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
