import random, string


def get_rand_alphanumeric(length: int=6, lowercase: bool=False) -> str:
    """Return random alphanumeric string"""
    if lowercase:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
