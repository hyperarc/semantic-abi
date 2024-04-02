from semanticabi.abi.item.Matches import EqualMatch, ExactInSetMatch, BoundMatch


def test_equal_matches():
    assert EqualMatch('from', 'to').matches({'from': '0x123'}, {'to': '0x123'})
    assert not EqualMatch('from', 'to').matches({'from': '0x123'}, {'to': '0x456'})
    assert not EqualMatch('from', 'to').matches({'from': '0x123'}, {'from': '0x123', 'to': '0x456'})


def test_exact_in_set_matches():
    assert ExactInSetMatch('from', {'from', 'to'}).matches({'from': '0x123'}, {'from': '0x123', 'to': '0x456'})
    assert ExactInSetMatch('from', {'from', 'to'}).matches({'from': '0x123'}, {'from': '0x456', 'to': '0x123'})
    assert not ExactInSetMatch('from', {'from', 'to'}).matches({'from': '0x123'}, {'from': '0x456', 'to': '0x789'})


def test_bounds_matches():
    # Check between upper and lower bounds
    assert BoundMatch('from', 'to', 0.5, 1.5).matches({'from': 2}, {'to': 1})
    assert BoundMatch('from', 'to', 0.5, 1.5).matches({'from': 2}, {'to': 2})
    assert BoundMatch('from', 'to', 0.5, 1.5).matches({'from': 2}, {'to': 3})
    assert not BoundMatch('from', 'to', 0.5, 1.5).matches({'from': 2}, {'to': 0})
    assert not BoundMatch('from', 'to', 0.5, 1.5).matches({'from': 2}, {'to': 4})

    # Check >= lower bound
    assert BoundMatch('from', 'to', 0.5, None).matches({'from': 2}, {'to': 1})
    assert BoundMatch('from', 'to', 0.5, None).matches({'from': 2}, {'to': 2})
    assert not BoundMatch('from', 'to', 0.5, None).matches({'from': 2}, {'to': 0})

    # Check <= upper bound
    assert BoundMatch('from', 'to', None, 1.5).matches({'from': 2}, {'to': 2})
    assert BoundMatch('from', 'to', None, 1.5).matches({'from': 2}, {'to': 3})
    assert not BoundMatch('from', 'to', None, 1.5).matches({'from': 2}, {'to': 4})
