#!/usr/bin/env python3
from read_grant import read_pkl
from grants_to_csv import reshape_grant
import pytest

P25 = read_pkl('data/2025.pkl')
def test_reshape():
    #p85 = read_pkl('data/1985.pkl')
    row = reshape_grant(P25[0])
    first = row[0]
    assert len(row) == 1
    assert len(first.keys()) >= 15
    assert first['po'][:4] == 'JONA'
    assert first['fiscal_year'] == 2025
