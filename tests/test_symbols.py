from formulation import Formulation

def test_ix_to_symbols():
    f1 = Formulation(0, 1)
    assert f1.ix_to_symbols(0) == [f1.Outcomes[0]]
    assert f1.ix_to_symbols(1) == [f1.Outcomes[1]]
    assert f1.ix_to_symbols(2) == [f1.Outcomes[2]]
    assert f1.ix_to_symbols(3) == [f1.Outcomes[0]]

    f2 = Formulation(0, 2)
    assert f2.ix_to_symbols(2) == [f2.Outcomes[0], f2.Outcomes[2]]
    assert f2.ix_to_symbols(3) == [f2.Outcomes[1], f2.Outcomes[0]]
    assert f2.ix_to_symbols(4) == [f2.Outcomes[1], f2.Outcomes[1]]
    assert f2.ix_to_symbols(5) == [f2.Outcomes[1], f2.Outcomes[2]]
    assert f2.ix_to_symbols(6) == [f2.Outcomes[2], f2.Outcomes[0]]
    assert f2.ix_to_symbols(7) == [f2.Outcomes[2], f2.Outcomes[1]]
    assert f2.ix_to_symbols(8) == [f2.Outcomes[2], f2.Outcomes[2]]
    assert f2.ix_to_symbols(9) == [f2.Outcomes[0], f2.Outcomes[0]]

def test_symbols_to_ix():
    f = Formulation(0, 1)
    assert f.symbols_to_ix([f.Outcomes[0]]) == 0
    assert f.symbols_to_ix([f.Outcomes[1]]) == 1
    assert f.symbols_to_ix([f.Outcomes[2]]) == 2
    assert f.symbols_to_ix([f.Outcomes[0], f.Outcomes[0]]) == 0
    assert f.symbols_to_ix([f.Outcomes[1], f.Outcomes[0]]) == 3
    assert f.symbols_to_ix([f.Outcomes[1], f.Outcomes[1]]) == 4
    assert f.symbols_to_ix([f.Outcomes[1], f.Outcomes[2]]) == 5
    assert f.symbols_to_ix([f.Outcomes[2], f.Outcomes[2], f.Outcomes[1], f.Outcomes[2]]) == 77

def test_roundtrip():
    for num_weighings in range(1, 5):
        f = Formulation(0, num_weighings)
        for ix in range(f.tt_rows):
            assert f.symbols_to_ix(f.ix_to_symbols(ix)) == ix

