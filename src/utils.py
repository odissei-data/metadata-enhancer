import asyncio

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


async def gather_with_concurrency(n, *coros):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros))
