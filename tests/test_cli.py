from oddball import main
from io import StringIO
from unittest.mock import patch
import pytest
import sys

def test_missing_args(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main()
    captured = capsys.readouterr()
    assert excinfo.type == SystemExit
    assert captured.err.startswith("usage")

def test_provided_args(capsys):
    testargs = ["oddball", "3", "2"]
    with patch.object(sys, 'argv', testargs):
        main()
    captured = capsys.readouterr()
    assert captured.out.startswith("Solving for 3 balls and 2 weighings")

def test_help(capsys):
    testargs = ["oddball", "-h"]
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as excinfo:
            main()
    captured = capsys.readouterr()
    assert excinfo.type == SystemExit
    assert captured.out.startswith("usage")
