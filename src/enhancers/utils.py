from fastapi import HTTPException


def _try_for_key(dictionary: dict, key_path: list, exception_detail: str):
    """ A function to retrieve a value from a nested dictionary.

    The function first sets value equal to dictionary and then loops through
    the key_path list, attempting to retrieve the value at each key.
    If the value cannot be retrieved due to a KeyError or TypeError,
    a HTTPException with a status code of 400 and the provided error message
    will be raised.

    :param dictionary: A dictionary object to traverse to retrieve a value.
    :param key_path: The keys to be traversed to retrieve a value.
    :param exception_detail: A string containing a custom error message.
    :return: The value at the end of the key path in the dictionary.
    """
    value = dictionary
    for key in key_path:
        try:
            value = value[key]
        except (KeyError, TypeError):
            raise HTTPException(status_code=422, detail=exception_detail)
    return value
