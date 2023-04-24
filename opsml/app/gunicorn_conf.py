from gunicorn.arbiter import Arbiter
from gunicorn.workers.base import Worker
from prometheus_client import multiprocess


def child_exit(_: Arbiter, worker: Worker) -> None:
    # Ensures prometheus cleans up .db files when a process exits.
    # See: https://github.com/prometheus/client_python/issues/275
    multiprocess.mark_process_dead(worker.pid)  # type: ignore[no-untyped-call]
