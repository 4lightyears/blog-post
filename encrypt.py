from passlib.hash import pbkdf2_sha256

def encrypt_pass(password):
    """takes in the non-hashed password as a parameter and returns the hashed version of it."""
    return pbkdf2_sha256.hash(password)

def verify_pass(password, hashed_pass):
    """takes in the user's password and hashed-password as parameter and compares them."""
    return pbkdf2_sha256.verify(password, hashed_pass)
