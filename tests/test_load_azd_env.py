from os import environ
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from dotenv_azd import load_azd_env, AzdCommandNotFoundError

class AzdEnvNewError(Exception):
    pass


class AzdEnvSetError(Exception):
    pass


def _azd_env_new(name: str, *, cwd: Path) -> str:
    result = subprocess.run(["azd", "env", "new", name], capture_output=True, text=True, cwd=cwd, check=False)
    if result.returncode:
        raise AzdEnvNewError("Failed to create azd env because of: " + result.stderr)
    return result.stdout


def _azd_env_set(key: str, value: str, *, cwd: Path) -> str:
    result = subprocess.run(["azd", "env", "set", key, value], capture_output=True, text=True, cwd=cwd, check=False)
    if result.returncode:
        raise AzdEnvSetError("Failed to set azd env value because of: " + result.stderr)
    return result.stdout


def test_load_azd_env(tmp_path: Path) -> None:
    from os import getenv

    with open(tmp_path / "azure.yaml", "w") as config:
        config.write("name: dotenv-azd-test\n")

    _azd_env_new("MY_AZD_ENV", cwd=tmp_path)
    var_set = load_azd_env(cwd=tmp_path)
    assert getenv("AZURE_ENV_NAME") == "MY_AZD_ENV"
    assert var_set


def test_load_azd_env_override(tmp_path: Path) -> None:
    from os import environ, getenv

    with open(tmp_path / "azure.yaml", "w") as config:
        config.write("name: dotenv-azd-test\n")

    environ["VAR1"] = "INITIAL"
    _azd_env_new("MY_AZD_ENV", cwd=tmp_path)
    _azd_env_set("VAR1", "OVERRIDE", cwd=tmp_path)
    var_set = load_azd_env(cwd=tmp_path)
    assert getenv("AZURE_ENV_NAME") == "MY_AZD_ENV"
    assert getenv("VAR1") == "INITIAL"
    assert var_set
    var_set = load_azd_env(cwd=tmp_path, override=True)
    assert getenv("VAR1") == "OVERRIDE"
    assert var_set


def test_load_azd_env_no_project_exists_error(tmp_path: Path) -> None:
    from dotenv_azd import AzdNoProjectExistsError

    with pytest.raises(AzdNoProjectExistsError, match="no project exists"):
        load_azd_env(cwd=tmp_path)


def test_load_azd_env_azd_command_not_found_error(tmp_path: Path) -> None:
    path = environ["PATH"]
    environ["PATH"] = ""
    with pytest.raises(AzdCommandNotFoundError):
        load_azd_env(cwd=tmp_path)
    environ["PATH"] = path


def test_load_azd_env_ignore_errors(tmp_path: Path) -> None:
    load_azd_env(cwd=tmp_path, quiet=True)


@patch("dotenv_azd.run")
@patch("dotenv_azd.shutil.which")
def test_cross_platform_command_not_found(mock_which, mock_run):
    """Test that FileNotFoundError is raised when the azd command is not found directly."""
    # Mock subprocess.run to raise FileNotFoundError when first called
    mock_run.side_effect = FileNotFoundError("No such file or directory: 'azd'")
    # Also mock shutil.which to return None (azd not in path)
    mock_which.return_value = None
    
    with pytest.raises(AzdCommandNotFoundError):
        load_azd_env()


@patch("dotenv_azd.run")
@patch("dotenv_azd.shutil.which")
def test_cross_platform_fallback_path_succeeds(mock_which, mock_run):
    """Test that the function falls back to using shutil.which to find azd."""
    # Mock subprocess.run to raise FileNotFoundError when first called, then succeed on second call
    mock_run.side_effect = [
        FileNotFoundError("No such file or directory: 'azd'"),
        subprocess.CompletedProcess(args=[], returncode=0, stdout="TEST_VAR=value", stderr="")
    ]
    # Mock shutil.which to return a path
    mock_which.return_value = "/mock/path/to/azd"
    
    # This should complete without raising an exception
    result = load_azd_env(override=True)
    assert result is True
    assert environ.get("TEST_VAR") == "value"


@patch("dotenv_azd.run")
def test_cross_platform_direct_call_succeeds(mock_run):
    """Test that the function works when the direct call to azd succeeds."""
    # Mock subprocess.run to return success
    mock_run.return_value = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="DIRECT_TEST_VAR=direct_value", stderr=""
    )
    
    # This should complete without raising an exception
    result = load_azd_env(override=True)
    assert result is True
    assert environ.get("DIRECT_TEST_VAR") == "direct_value"
