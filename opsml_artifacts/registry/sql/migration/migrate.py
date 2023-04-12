import os
import pathlib

import alembic.config

dir_path = pathlib.Path(__file__).parent.resolve()


def run_alembic():
    alembicArgs = [
        "--raiseerr",
        "upgrade",
        "head",
    ]
    os.chdir(dir_path)
    alembic.config.main(argv=alembicArgs)
