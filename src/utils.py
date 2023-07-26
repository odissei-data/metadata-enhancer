import asyncio
import csv

import jmespath
import requests
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


def load_tsv_from_github_raw(url):
    """ Loads a table from a tsv file fetched using a GitHub raw url.
    TODO: Right now the first column of the tsv file is empty.
        The code reflects this, but to be used universally the table
        and this code should be fixed to expect a first column.
    :param url: The GitHub raw url.
    :return: a dict with the dsc title as key and frequency of use as value.
    """
    response = requests.get(url)
    lines = response.text.strip().split('\n')
    reader = csv.reader(lines, delimiter='\t')
    next(reader)  # Skip the header row
    data_dict = {}
    for row in reader:
        row = [item.strip() for item in row if item.strip()]
        if len(row) >= 5:
            key = row[0]
            value = row[-1]
            data_dict[key] = value
    return data_dict
