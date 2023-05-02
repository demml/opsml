from opsml.deploy.loader import ModelLoader, Model


def test_models():
    models = ModelLoader().model_files
    loader = Model(model_path=models[0])
