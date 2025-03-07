from oddball import ix_to_symbols, symbols_to_ix, Outcomes

def test_ix_to_symbols():
    assert ix_to_symbols(0, 1) == [Outcomes[0]]
    assert ix_to_symbols(1, 1) == [Outcomes[1]]
    assert ix_to_symbols(2, 1) == [Outcomes[2]]
    assert ix_to_symbols(3, 1) == [Outcomes[0]]
    assert ix_to_symbols(2, 2) == [Outcomes[0], Outcomes[2]]
    assert ix_to_symbols(3, 2) == [Outcomes[1], Outcomes[0]]
    assert ix_to_symbols(4, 2) == [Outcomes[1], Outcomes[1]]
    assert ix_to_symbols(5, 2) == [Outcomes[1], Outcomes[2]]
    assert ix_to_symbols(6, 2) == [Outcomes[2], Outcomes[0]]
    assert ix_to_symbols(7, 2) == [Outcomes[2], Outcomes[1]]
    assert ix_to_symbols(8, 2) == [Outcomes[2], Outcomes[2]]
    assert ix_to_symbols(9, 2) == [Outcomes[0], Outcomes[0]]

def test_symbols_to_ix():
    assert symbols_to_ix([Outcomes[0]]) == 0
    assert symbols_to_ix([Outcomes[1]]) == 1
    assert symbols_to_ix([Outcomes[2]]) == 2
    assert symbols_to_ix([Outcomes[0], Outcomes[0]]) == 0
    assert symbols_to_ix([Outcomes[1], Outcomes[0]]) == 3
    assert symbols_to_ix([Outcomes[1], Outcomes[1]]) == 4
    assert symbols_to_ix([Outcomes[1], Outcomes[2]]) == 5
    assert symbols_to_ix([Outcomes[2], Outcomes[2], Outcomes[1], Outcomes[2]]) == 77

def test_roundtrip():
    for num_weighings in range(1, 5):
        tt_rows = len(Outcomes) ** num_weighings
        for ix in range(tt_rows):
            assert symbols_to_ix(ix_to_symbols(ix, num_weighings)) == ix
