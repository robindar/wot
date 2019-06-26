import pandas as pd
import wot.io

def test_read_day_pairs_from_file():
    data = [ [ 0, 1, 50 ], [ 1, 2, 80 ], [ 2, 4, 30 ], [ 4, 5, 10 ] ]
    expected_pairs = pd.DataFrame(data, columns=[ "t0", "t1", "lambda1" ])
    read_pairs = wot.io.read_day_pairs("test/resources/day_pairs_example.txt")
    assert (read_pairs.columns == expected_pairs.columns).all()
    assert (read_pairs == expected_pairs).all().all()

def test_read_day_pairs_from_string():
    pairs_string = "t0,t1,lambda1;0,1,50;1,2,80;2,4,30;4,5,10"
    data = [ [ 0, 1, 50 ], [ 1, 2, 80 ], [ 2, 4, 30 ], [ 4, 5, 10 ] ]
    expected_pairs = pd.DataFrame(data, columns=[ "t0", "t1", "lambda1" ])
    read_pairs = wot.io.read_day_pairs(pairs_string)
    assert (read_pairs.columns == expected_pairs.columns).all()
    assert (read_pairs == expected_pairs).all().all()
