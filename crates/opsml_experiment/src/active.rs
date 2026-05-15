//! Active experiment stack.
//!
//! Scope: SINGLE-THREADED. Concurrent experiments per process are not
//! supported by the fluent free functions. Concurrent users must use the
//! explicit `exp.log_metric(...)` form on a captured `Experiment`.
//!
//! TODO(threading): migrate to a `contextvars`-backed thread/task-local stack
//! in a follow-up slice once usage justifies the extra boundary complexity.

use crate::error::ExperimentError;
use crate::experiment::Experiment;
use pyo3::prelude::*;
use std::sync::{Mutex, OnceLock};

pub struct ActiveStack<T> {
    inner: Mutex<Vec<T>>,
}

impl<T> Default for ActiveStack<T> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T> ActiveStack<T> {
    pub const fn new() -> Self {
        Self {
            inner: Mutex::new(Vec::new()),
        }
    }

    pub fn push(&self, value: T) -> Result<(), ExperimentError> {
        self.inner
            .lock()
            .map_err(|_| ExperimentError::ActiveStackPoisoned)?
            .push(value);
        Ok(())
    }

    pub fn depth(&self) -> Result<usize, ExperimentError> {
        Ok(self
            .inner
            .lock()
            .map_err(|_| ExperimentError::ActiveStackPoisoned)?
            .len())
    }

    pub fn pop(&self) -> Result<Option<T>, ExperimentError> {
        Ok(self
            .inner
            .lock()
            .map_err(|_| ExperimentError::ActiveStackPoisoned)?
            .pop())
    }

    pub fn with_top<R>(&self, f: impl FnOnce(&T) -> R) -> Result<Option<R>, ExperimentError> {
        let guard = self
            .inner
            .lock()
            .map_err(|_| ExperimentError::ActiveStackPoisoned)?;
        Ok(guard.last().map(f))
    }
}

struct ActiveExperiment {
    uid: String,
    exp: Py<Experiment>,
}

static ACTIVE: OnceLock<ActiveStack<ActiveExperiment>> = OnceLock::new();

fn stack() -> &'static ActiveStack<ActiveExperiment> {
    ACTIVE.get_or_init(ActiveStack::new)
}

pub fn push(exp: Py<Experiment>, py: Python<'_>) -> Result<(), ExperimentError> {
    let uid = exp.borrow(py).uid().to_string();
    stack().push(ActiveExperiment { uid, exp })
}

pub fn pop(_py: Python<'_>, expected_uid: &str) -> Result<Option<Py<Experiment>>, ExperimentError> {
    let popped = stack().pop()?;
    if let Some(active) = popped {
        if active.uid != expected_uid {
            tracing::warn!(
                expected = expected_uid,
                actual = %active.uid,
                "active experiment stack pop mismatch"
            );
        }
        Ok(Some(active.exp))
    } else {
        Ok(None)
    }
}

pub fn current(py: Python<'_>) -> Result<Py<Experiment>, ExperimentError> {
    stack()
        .with_top(|active| active.exp.clone_ref(py))?
        .ok_or(ExperimentError::NoActiveExperiment)
}

pub fn depth() -> Result<usize, ExperimentError> {
    stack().depth()
}
