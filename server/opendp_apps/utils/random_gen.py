import random, string


def random_alphanum(num_chars=6):
    """Generate a random alphanumeric string in lowercase"""
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                  for _ in range(num_chars))