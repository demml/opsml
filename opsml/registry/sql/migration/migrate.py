import os
import pathlib
from contextlib import contextmanager

import alembic.config

dir_path = pathlib.Path(__file__).parent.resolve()


@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def run_alembic_migrations() -> str:
    alembicArgs = [
        "--raiseerr",
        "upgrade",
        "head",
    ]
    with cwd(dir_path) as alembic_path:
        alembic.config.main(argv=alembicArgs)

    return "Success!"
