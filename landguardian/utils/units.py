"""
Unit conversion utilities for LandGuardian.
"""

def convert_units(value, from_unit, to_unit, unit_type):
    """
    Convert between different units.

    Args:
        value (float): The value to convert
        from_unit (str): The source unit
        to_unit (str): The target unit
        unit_type (str): The type of unit ('area', 'temperature', 'distance')

    Returns:
        float: The converted value

    Raises:
        ValueError: If conversion is not supported
    """
    if unit_type == 'area':
        return _convert_area(value, from_unit, to_unit)
    elif unit_type == 'temperature':
        return _convert_temperature(value, from_unit, to_unit)
    elif unit_type == 'distance':
        return _convert_distance(value, from_unit, to_unit)
    else:
        raise ValueError(f"Unsupported unit type: {unit_type}")

def _convert_area(value, from_unit, to_unit):
    """Convert area units."""
    # Base unit: square meters
    conversions = {
        'sq_m': 1,
        'sq_km': 1000000,
        'hectares': 10000,
        'acres': 4046.86,
        'sq_ft': 0.092903,
        'sq_yd': 0.836127
    }

    if from_unit not in conversions or to_unit not in conversions:
        raise ValueError(f"Unsupported area units: {from_unit} to {to_unit}")

    # Convert to base unit then to target
    base_value = value * conversions[from_unit]
    return base_value / conversions[to_unit]

def _convert_temperature(value, from_unit, to_unit):
    """Convert temperature units."""
    if from_unit == 'celsius' and to_unit == 'fahrenheit':
        return (value * 9/5) + 32
    elif from_unit == 'fahrenheit' and to_unit == 'celsius':
        return (value - 32) * 5/9
    elif from_unit == to_unit:
        return value
    else:
        raise ValueError(f"Unsupported temperature conversion: {from_unit} to {to_unit}")

def _convert_distance(value, from_unit, to_unit):
    """Convert distance units."""
    # Base unit: meters
    conversions = {
        'm': 1,
        'km': 1000,
        'ft': 0.3048,
        'yd': 0.9144,
        'mi': 1609.34
    }

    if from_unit not in conversions or to_unit not in conversions:
        raise ValueError(f"Unsupported distance units: {from_unit} to {to_unit}")

    # Convert to base unit then to target
    base_value = value * conversions[from_unit]
    return base_value / conversions[to_unit]