import logging

LOGGER = logging.getLogger("config.password_reader")


def password(user, password_dir):
    """
    Fetches the user's password from disk.
    :param str user: the username for which to get the password
    :param Path password_dir: the directory in which the password is stored
    :return str: the password stored on disk for that user
    """
    pwd_file = password_dir / (user + "_pass.txt")
    if not pwd_file.exists():
        LOGGER.error("the password for %(user)s was not found on disk", {"user": user})
        return None
    return pwd_file.read_text().strip()
