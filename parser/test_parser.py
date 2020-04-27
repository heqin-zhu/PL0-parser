import os
from parser import *
from token_scanner import *


def test_parser():
    data = [
        'begin ++1--1;1<<2+3%2;2&1;end.',
        '-1+2*3/%2.',
        '4!!.',
        'if   0 then 1 elif 1>2 then 2 else 3.',
    ]
    results = [
        [2,8,0],
        [2.0],
        [620448401733239439360000],
        [3.0],
    ]
    parser = PL0()
    for s, res in zip(data, results):
        assert res == parser.parse(list(genToken(s)))


def test_file():
    for path in os.listdir('./scripts'):
        print(path)
        run('scripts/'+path)


if __name__ == "__main__":
    test_parser()
    test_file()
