from unittest.mock import patch

import pytest

import missing_license.auth as auth_module


def test_authenticate_with_token(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "fake-token")
    monkeypatch.delenv("APP_ID", raising=False)

    with (
        patch.object(auth_module.github.Auth, "Token") as mock_token_cls,
        patch.object(auth_module, "Github") as mock_gh,
    ):
        auth_module.authenticate()
        mock_token_cls.assert_called_once_with("fake-token")
        mock_gh.assert_called_once_with(auth=mock_token_cls.return_value)


def test_authenticate_with_app(monkeypatch):
    monkeypatch.setenv("APP_ID", "123")
    monkeypatch.setenv("APP_PRIVATE_KEY", "fake-key")
    monkeypatch.setenv("APP_INSTALLATION_ID", "456")
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with (
        patch.object(auth_module.github.Auth, "AppAuth") as mock_app_auth,
        patch.object(
            auth_module.github.Auth, "AppInstallationAuth"
        ) as mock_install_auth,
        patch.object(auth_module, "Github") as mock_gh,
    ):
        auth_module.authenticate()
        mock_app_auth.assert_called_once_with(123, "fake-key")
        mock_install_auth.assert_called_once_with(mock_app_auth.return_value, 456)
        mock_gh.assert_called_once_with(auth=mock_install_auth.return_value)


def test_authenticate_no_credentials(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("APP_ID", raising=False)

    with pytest.raises(ValueError, match="No authentication credentials found"):
        auth_module.authenticate()
