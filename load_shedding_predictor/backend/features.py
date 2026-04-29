"""
Feature definitions for load shedding prediction inference.
Zone encoding and temperature settings.
"""

ZONE_MAPPING = {
    'Gulberg': 0, 'Model Town': 1, 'Cantt': 2, 'Shalimar': 3,
    'Samanabad': 4, 'Allama Iqbal Town': 5, 'Data Gunj Baksh': 6,
    'Ravi Road': 7, 'Shahalam': 8, 'Mughalpura': 9, 'Outfall Road': 10,
    'Nishtar Town': 11, 'Wahdat Colony': 12, 'Sabzazar': 13, 'Yunus Road': 14,
    'Cantonment': 15, 'Johar Town': 16, 'Wapda Town': 17, 'Muslim Town': 18,
    'Kahnpur': 19, 'Shahpur': 20, 'Harbanspura': 21, 'Ferozewala': 22
}

DEFAULT_TEMPERATURE = 20.0


def get_zone_list():
    """Get list of available zones."""
    return list(ZONE_MAPPING.keys())


if __name__ == "__main__":
    print("Available zones:")
    for zone, code in ZONE_MAPPING.items():
        print(f"  {zone}: {code}")