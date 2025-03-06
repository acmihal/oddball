from oddball import main
from io import StringIO
import sys

def test_main_output(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello, world!\n"
