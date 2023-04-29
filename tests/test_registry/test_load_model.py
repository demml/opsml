from click.testing import CliRunner
from opsml.scripts.load_model_card import load_model_card_to_file
from opsml.model.types import ModelDownloadInfo
from unittest.mock import patch, MagicMock


def test_cli_class(db_registries, mock_model_cli_loader, test_model_card, mock_pathlib):
    with patch.multiple(
        "opsml.registry.sql.registry.CardRegistry",
        load_card=MagicMock(return_value=test_model_card),
    ):

        model_info = ModelDownloadInfo(
            name="driven_drop_off_predictor",
            team="SPMS",
            version="1.0.0",
            uid="test",
        )

        model_registry = db_registries["model"]
        loader = mock_model_cli_loader(
            model_info=model_info,
            registry=model_registry,
        )

        loader.save_to_local_file()


def test_load_model_card_version(mock_model_cli_loader, test_model_card, mock_pathlib):

    with patch.multiple(
        "opsml.registry.sql.registry.CardRegistry",
        load_card=MagicMock(return_value=test_model_card),
    ):
        args1 = ["--name", "driven_drop_off_predictor", "--team", "SPMS", "--version", "2"]
        args2 = ["--name", "driven_drop_off_predictor", "--team", "SPMS", "--version", "2", "--version", "3"]
        args3 = ["--name", "driven_drop_off_predictor", "--uid", "blah"]

        for arg_list in [args1, args2, args3]:
            runner = CliRunner()
            result = runner.invoke(load_model_card_to_file, arg_list)
            assert result.exit_code == 0
