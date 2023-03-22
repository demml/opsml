def test_semvar(db_registries):
    model_registry = db_registries["model"]

    for i in range(0, 10):
        expected_version = f"1.{i+1}.0"
        new_version = model_registry.registry._increment_version(version=f"1.{i}.0", version_type="minor")

        assert expected_version == new_version
