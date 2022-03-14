import random, string


def get_rand_alphanumeric(length: int=6, lowercase: bool=False) -> str:
    """Return random alphanumeric string"""
    if lowercase:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def random_with_n_digits(n):
    """Get random digits"""
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return random.randint(range_start, range_end)
