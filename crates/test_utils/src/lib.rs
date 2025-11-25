#[macro_export]
macro_rules! retry_flaky_test {
    ($attempts:expr, $delay_ms:expr, $test_logic:block) => {{
        use std::panic::UnwindSafe;
        use tokio::task::JoinHandle;
        use tokio::time::{self, Duration};

        const MAX_ATTEMPTS: usize = $attempts;
        const RETRY_DELAY: Duration = Duration::from_millis($delay_ms);

        let test_fn = || async move { $test_logic };

        for attempt in 1..=MAX_ATTEMPTS {
            let handle: JoinHandle<()> = tokio::task::spawn(test_fn());
            let result = handle.await;

            match result {
                Ok(_) => {
                    return;
                }

                Err(e) if e.is_panic() => {
                    if attempt < MAX_ATTEMPTS {
                        eprintln!(
                            "Flaky test attempt {} failed (Task Panic). Retrying in {:?}...",
                            attempt, RETRY_DELAY
                        );
                        time::sleep(RETRY_DELAY).await;
                    } else {
                        eprintln!(
                            "Flaky test failed on final attempt {}. Max retries reached.",
                            attempt
                        );
                        if let Ok(panic_payload) = e.try_into_panic() {
                            std::panic::resume_unwind(panic_payload);
                        } else {
                            panic!("Task panicked but could not recover payload on final retry.");
                        }
                    }
                }
                Err(e) => {
                    eprintln!(
                        "Test failed with unexpected JoinError (not a panic): {:?}",
                        e
                    );
                    panic!(
                        "Task failed due to cancellation or unexpected error: {:?}",
                        e
                    );
                }
            }
        }
    }};

    // Default invocation
    ($test_logic:block) => {
        retry_flaky_test!(3, 1000, $test_logic)
    };
}
