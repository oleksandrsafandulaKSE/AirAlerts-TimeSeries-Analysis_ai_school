from src import regions


def test_exactly_24_unique_units():
    assert len(regions.UNITS) == 24
    names = [v["official_name"] for v in regions.UNITS.values()]
    uids = [v["api_uid"] for v in regions.UNITS.values()]
    assert len(set(names)) == 24 and len(set(uids)) == 24


def test_uid_set_and_kyiv_ids():
    expected = {3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 31}
    assert {v["api_uid"] for v in regions.UNITS.values()} == expected
    assert regions.UNITS["kyivska"]["api_uid"] == 14
    assert regions.UNITS["kyiv_city"]["api_uid"] == 31


def test_groups_d011():
    groups = {k: v["group"] for k, v in regions.UNITS.items()}
    frontline = {"chernihivska", "sumska", "kharkivska", "donetska", "dnipropetrovska",
                 "zaporizka", "khersonska", "mykolaivska"}
    assert {k for k, g in groups.items() if g == "frontline"} == frontline
    assert [k for k, g in groups.items() if g == "kyiv_city"] == ["kyiv_city"]
    assert sum(g == "rear" for g in groups.values()) == 15
    assert groups["kyivska"] == "rear"


def test_luhanska_excluded_and_mapping():
    assert "Luhanska oblast" in regions.EXCLUDED
    assert all("luhansk" not in k for k in regions.UNITS)
    assert regions.unit_from_official("Kyiv City") == "kyiv_city"
    assert regions.unit_from_official("Kyivska oblast") == "kyivska"


def test_unknown_name_raises():
    import pytest
    with pytest.raises(KeyError):
        regions.unit_from_official("Kyiv")


def test_neighbours_symmetric_and_kyiv():
    for k, ns in regions.NEIGHBOURS.items():
        assert k not in ns
        for n in ns:
            assert n in regions.UNITS and k in regions.NEIGHBOURS[n]
    assert regions.NEIGHBOURS["kyiv_city"] == {"kyivska"}
    assert "kyiv_city" in regions.NEIGHBOURS["kyivska"]
