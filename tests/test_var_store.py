from opsml_data.var_store.store import DependentVarStore


def test_var_store_stop(test_sql_file):
    var_store = DependentVarStore(
        level="stop",
        dependent_vars=["drop_off"],
        sql_file=test_sql_file,
    )
    df = var_store.pull_data()
    assert "DROP_OFF_TIME" in df.columns


def test_var_store_bundle(test_sql_file):

    var_store = DependentVarStore(
        level="bundle",
        dependent_vars=["checkout"],
        sql_file=test_sql_file,
    )
    df = var_store.pull_data()

    assert "BUNDLE_CHECKOUT_TIME" in df.columns

    # test multiple
    var_store = DependentVarStore(
        level="bundle",
        dependent_vars=["checkout", "delivery"],
        sql_file=test_sql_file,
    )
    df = var_store.pull_data()

    assert "BUNDLE_CHECKOUT_TIME" in df.columns
    assert "BUNDLE_DELIVERY_TIME" in df.columns


def test_var_store_order(var_store_order_query):

    var_store = DependentVarStore(
        level="order",
        dependent_vars=["checkout"],
        query=var_store_order_query,
    )
    df = var_store.pull_data()

    assert "CHECKOUT_TIME" in df.columns

    # test multiple
    var_store = DependentVarStore(
        level="order",
        dependent_vars=["checkout", "delivery", "drop_off"],
        query=var_store_order_query,
    )
    df = var_store.pull_data()

    assert "CHECKOUT_TIME" in df.columns
    assert "DELIVERY_TIME" in df.columns
    assert "DROP_OFF_TIME" in df.columns
