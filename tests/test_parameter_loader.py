from utils.parameter_loader import flatten_dict


def test_flatten_dict_simple():
    d = {"a": 1, "b": 2}
    result = flatten_dict(d)
    assert result == {"a": 1, "b": 2}


def test_flatten_dict_nested():
    d = {"section": {"param1": 10, "param2": 20}}
    result = flatten_dict(d)
    assert "section" in result
    assert result["section"] is None
    assert "\tparam1" in result
    assert result["\tparam1"] == 10
    assert "\tparam2" in result
    assert result["\tparam2"] == 20


def test_flatten_dict_deep_nested():
    d = {"outer": {"inner": {"value": 42}}}
    result = flatten_dict(d)
    assert result["outer"] is None
    assert result["\tinner"] is None
    assert result["\t\tvalue"] == 42


def test_flatten_dict_empty():
    assert flatten_dict({}) == {}


def test_flatten_dict_mixed():
    d = {"top_level": 5, "section": {"nested": 10}}
    result = flatten_dict(d)
    assert result["top_level"] == 5
    assert result["section"] is None
    assert result["\tnested"] == 10
