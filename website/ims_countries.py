"""ISO 3166-1 alpha-3 codes for Swan IMS travel insurance."""

try:
    import pycountry
except ImportError:
    pycountry = None

# Fallback if pycountry is unavailable
_FALLBACK = [
    ('LBN', 'Lebanon'), ('FRA', 'France'), ('ARE', 'United Arab Emirates'),
    ('TUR', 'Turkey'), ('GBR', 'United Kingdom'), ('USA', 'United States'),
    ('DEU', 'Germany'), ('ITA', 'Italy'), ('ESP', 'Spain'), ('GRC', 'Greece'),
    ('EGY', 'Egypt'), ('JOR', 'Jordan'), ('SAU', 'Saudi Arabia'), ('QAT', 'Qatar'),
    ('IND', 'India'), ('THA', 'Thailand'), ('MYS', 'Malaysia'), ('SGP', 'Singapore'),
    ('CAN', 'Canada'), ('AUS', 'Australia'), ('CHE', 'Switzerland'), ('NLD', 'Netherlands'),
]


def iso3_countries() -> list[tuple[str, str]]:
    if pycountry:
        rows = [(c.alpha_3, c.name) for c in pycountry.countries if hasattr(c, 'alpha_3')]
        return sorted(rows, key=lambda item: item[1])
    return sorted(_FALLBACK, key=lambda item: item[1])


def country_name(iso3: str) -> str:
    code = (iso3 or '').upper()
    for c_code, name in iso3_countries():
        if c_code == code:
            return name
    return code
