import logging
import pickle
from pathlib import Path

LOGGER = logging.getLogger('dump')


def load_from_cache(pickled_path: Path, bytes_fn):
    """
    If the given path has a pickled object, load it. Else, call the function and dump the result
    to the given file.

    :param pickled_path: the path where the result is (or should be) cached
    :param bytes_fn: the function to call to get the object
    :return: the object (cached or not)
    """
    if pickled_path.exists():
        LOGGER.debug(f"Loading from cached value {pickled_path}")
        obj = pickle.load(pickled_path.open("rb"))
    else:
        LOGGER.info(f"Cached value not found at {pickled_path}, loading value...")
        obj = bytes_fn()
        pickle.dump(obj, pickled_path.open("wb+"))
    return obj
