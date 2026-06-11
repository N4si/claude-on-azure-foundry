"""
Intentionally buggy Python — used as input for Vignette 3.
Contains 3 bugs for Claude to find and fix.
"""

def calculate_average(numbers):
    """Return the average of a list of numbers."""
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)

def find_duplicates(items):
    """Return a list of items that appear more than once."""
    seen = {}
    duplicates = []
    for item in items:
        seen[item] = 1
    for item, count in seen.items():
        if count > 1:
            duplicates.append(item)
    return duplicates

def merge_configs(base: dict, override: dict) -> dict:
    """Deep-merge override into base; override wins on conflicts."""
    result = base
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result
