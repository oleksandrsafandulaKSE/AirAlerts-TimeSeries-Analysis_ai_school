"""The single table of the 24 forecast units. The ONLY place names are mapped (D-017 #1)."""

# key, official English name (verbatim from official_data_en.csv), alerts.in.ua UID, group (D-011)
_UNITS = [
    ("kyiv_city", "Kyiv City", 31, "kyiv_city"),
    ("chernihivska", "Chernihivska oblast", 25, "frontline"),
    ("sumska", "Sumska oblast", 20, "frontline"),
    ("kharkivska", "Kharkivska oblast", 22, "frontline"),
    ("donetska", "Donetska oblast", 28, "frontline"),
    ("dnipropetrovska", "Dnipropetrovska oblast", 9, "frontline"),
    ("zaporizka", "Zaporizka oblast", 12, "frontline"),
    ("khersonska", "Khersonska oblast", 23, "frontline"),
    ("mykolaivska", "Mykolaivska oblast", 17, "frontline"),
    ("kyivska", "Kyivska oblast", 14, "rear"),
    ("zhytomyrska", "Zhytomyrska oblast", 10, "rear"),
    ("vinnytska", "Vinnytska oblast", 4, "rear"),
    ("cherkaska", "Cherkaska oblast", 24, "rear"),
    ("poltavska", "Poltavska oblast", 19, "rear"),
    ("kirovohradska", "Kirovohradska oblast", 15, "rear"),
    ("odeska", "Odeska oblast", 18, "rear"),
    ("khmelnytska", "Khmelnytska oblast", 3, "rear"),
    ("rivnenska", "Rivnenska oblast", 5, "rear"),
    ("volynska", "Volynska oblast", 8, "rear"),
    ("lvivska", "Lvivska oblast", 27, "rear"),
    ("ternopilska", "Ternopilska oblast", 21, "rear"),
    ("ivano_frankivska", "Ivano-Frankivska oblast", 13, "rear"),
    ("zakarpatska", "Zakarpatska oblast", 11, "rear"),
    ("chernivetska", "Chernivetska oblast", 26, "rear"),
]

# Excluded on purpose (D-008): official name -> reason. Crimea/Sevastopol are not in the official file.
EXCLUDED = {"Luhanska oblast": "permanent alert since 2022-04-04 (D-008)"}

# Shared land borders between the 24 units (hard-coded, D-017). To be checked by the human before M2.
_BORDERS = [
    ("kyiv_city", "kyivska"),
    ("kyivska", "zhytomyrska"), ("kyivska", "vinnytska"), ("kyivska", "cherkaska"),
    ("kyivska", "poltavska"), ("kyivska", "chernihivska"),
    ("chernihivska", "sumska"), ("chernihivska", "poltavska"),
    ("sumska", "poltavska"), ("sumska", "kharkivska"),
    ("kharkivska", "poltavska"), ("kharkivska", "dnipropetrovska"), ("kharkivska", "donetska"),
    ("donetska", "dnipropetrovska"), ("donetska", "zaporizka"),
    ("dnipropetrovska", "poltavska"), ("dnipropetrovska", "zaporizka"),
    ("dnipropetrovska", "khersonska"), ("dnipropetrovska", "mykolaivska"),
    ("dnipropetrovska", "kirovohradska"),
    ("zaporizka", "khersonska"),
    ("khersonska", "mykolaivska"),
    ("mykolaivska", "kirovohradska"), ("mykolaivska", "odeska"),
    ("odeska", "kirovohradska"), ("odeska", "vinnytska"),
    ("kirovohradska", "poltavska"), ("kirovohradska", "cherkaska"), ("kirovohradska", "vinnytska"),
    ("poltavska", "cherkaska"),
    ("cherkaska", "vinnytska"),
    ("vinnytska", "zhytomyrska"), ("vinnytska", "khmelnytska"), ("vinnytska", "chernivetska"),
    ("zhytomyrska", "khmelnytska"), ("zhytomyrska", "rivnenska"),
    ("khmelnytska", "chernivetska"), ("khmelnytska", "ternopilska"), ("khmelnytska", "rivnenska"),
    ("rivnenska", "volynska"), ("rivnenska", "lvivska"), ("rivnenska", "ternopilska"),
    ("volynska", "lvivska"),
    ("lvivska", "ternopilska"), ("lvivska", "ivano_frankivska"), ("lvivska", "zakarpatska"),
    ("ternopilska", "chernivetska"), ("ternopilska", "ivano_frankivska"),
    ("ivano_frankivska", "chernivetska"), ("ivano_frankivska", "zakarpatska"),
    ("chernivetska", "zakarpatska"),
]

UNITS = {k: {"official_name": n, "api_uid": u, "group": g} for k, n, u, g in _UNITS}
NEIGHBOURS = {k: set() for k in UNITS}
for _a, _b in _BORDERS:
    NEIGHBOURS[_a].add(_b)
    NEIGHBOURS[_b].add(_a)
_BY_OFFICIAL = {v["official_name"]: k for k, v in UNITS.items()}


def units():
    return list(UNITS)


def group_of(key):
    return UNITS[key]["group"]


def unit_from_official(name):
    """Exact lookup; an unknown name raises KeyError (no fuzzy matching)."""
    if name not in _BY_OFFICIAL:
        raise KeyError(f"unknown official oblast name: {name!r}")
    return _BY_OFFICIAL[name]
