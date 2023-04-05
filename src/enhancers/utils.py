import jmespath
from fastapi import HTTPException
from jmespath.exceptions import JMESPathError


def _try_for_key(dictionary: dict, key_path: str):
    """ A function to retrieve a value from a nested dictionary.

    """
    try:
        return jmespath.search(key_path, dictionary)
    except JMESPathError as error:
        raise HTTPException(status_code=422, detail=str(error))
