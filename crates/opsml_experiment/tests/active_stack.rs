use opsml_experiment::active::ActiveStack;

#[test]
fn active_stack_push_then_top_returns_value() {
    let s = ActiveStack::<String>::new();
    s.push("a".into()).unwrap();
    let got = s.with_top(|v| v.clone()).unwrap();
    assert_eq!(got, Some("a".to_string()));
}

#[test]
fn active_stack_push_two_pop_returns_last() {
    let s = ActiveStack::<String>::new();
    s.push("a".into()).unwrap();
    s.push("b".into()).unwrap();
    assert_eq!(s.pop().unwrap(), Some("b".into()));
    assert_eq!(s.pop().unwrap(), Some("a".into()));
}

#[test]
fn active_stack_pop_empty_returns_none() {
    let s = ActiveStack::<String>::new();
    assert_eq!(s.pop().unwrap(), None);
}

#[test]
fn active_stack_depth_reflects_push_pop() {
    let s = ActiveStack::<String>::new();
    assert_eq!(s.depth().unwrap(), 0);
    s.push("a".into()).unwrap();
    s.push("b".into()).unwrap();
    assert_eq!(s.depth().unwrap(), 2);
    s.pop().unwrap();
    assert_eq!(s.depth().unwrap(), 1);
}
