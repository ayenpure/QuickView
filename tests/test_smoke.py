"""Smoke tests that need no GUI, display, or data files.

They require the QuickView dependencies (including ParaView's Python
modules) to be installed, e.g. the environment from ``quickview-env.yml``.
"""

import subprocess
import sys

import pytest

pytest.importorskip("paraview.simple", reason="ParaView Python modules not found")


def test_package_metadata():
    import quickview

    assert quickview.__version__
    assert quickview.__license__


def test_modules_import():
    import quickview.interface
    import quickview.pipeline
    import quickview.view_manager

    assert hasattr(quickview.pipeline, "EAMVisSource")
    assert hasattr(quickview.interface, "EAMApp")


def test_vis_source_builds():
    from quickview.pipeline import EAMVisSource

    source = EAMVisSource()
    assert source.valid is False
    assert source.data_file is None
    assert source.conn_file is None


def test_app_object_builds():
    from quickview.interface import EAMApp
    from quickview.pipeline import EAMVisSource

    app = EAMApp(EAMVisSource(), workdir=".")
    assert app.server is not None


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "quickview.app", "--help"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0
    for option in ("--conn", "--data", "--state", "--workdir"):
        assert option in result.stdout
