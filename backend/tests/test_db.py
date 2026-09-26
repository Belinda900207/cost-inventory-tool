from unittest.mock import MagicMock

from app import db
from app.config import Settings


def test_database_probe_executes_select_one(monkeypatch):
    engine = MagicMock()
    monkeypatch.setattr(db, "get_engine", lambda: engine)
    db.check_database()
    connection = engine.connect.return_value.__enter__.return_value
    assert str(connection.execute.call_args.args[0]) == "SELECT 1"
    engine.connect.return_value.__exit__.assert_called_once()


def test_settings_hide_password_and_encode_url():
    settings = Settings(
        _env_file=None,
        mysql_user="probe",
        mysql_password="test/@%:value",
        mysql_database="probe_test",
    )
    assert "test/@%:value" not in repr(settings)
    assert settings.database_url.password == "test/@%:value"
    assert "test/@%:value" not in str(settings.database_url)
