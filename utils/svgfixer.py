# brew install svgo

import glob
import os
import shutil
import sys

from common import local, project_dir


def main(argv):
    os.chdir(project_dir)

    matches = glob.glob("mkdocs/**/*.svg", recursive=True)
    for match in matches:
        print(f"Optimizing {match} ..")
        print(local(f"svgo {match} -o tmp.svg"))
        shutil.move("tmp.svg", match)


if __name__ == "__main__":
    main(sys.argv)
