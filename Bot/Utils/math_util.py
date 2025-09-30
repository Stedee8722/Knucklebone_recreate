import math

# rounding a number up only if it's bigger than 0.5
def rounding(num:float) -> int:
    """Rounds a number to the nearest integer, with special handling for .5 cases.
    If the number is exactly .5, it rounds up if positive and down if negative.
    Args:
        num (float): The number to round.
    Returns:
        int: The rounded integer.
    """
    if num % 1 == 0.5:
        if num < 0: return math.floor(num)
        elif num > 0: return math.ceil(num)
    else: return round(num)