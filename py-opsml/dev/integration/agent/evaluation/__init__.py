from typing import Any


def run_offline_evaluation() -> Any:
    from .evaluate import run_offline_evaluation as _run_offline_evaluation

    return _run_offline_evaluation()


def __getattr__(name: str) -> Any:
    if name == "GoogleAdkEvalOrchestrator":
        from .evaluate import GoogleAdkEvalOrchestrator

        return GoogleAdkEvalOrchestrator
    raise AttributeError(name)


__all__ = ["GoogleAdkEvalOrchestrator", "run_offline_evaluation"]
