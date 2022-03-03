from csv import DictReader, writer, reader
from re import sub
from unicodedata import normalize
from time import perf_counter


def timing(function):
    def new_func(*a, **k):
        tic = perf_counter()
        res = function(*a, **k)
        toc = perf_counter()
        print(f'[ timing ] {function.__name__} took {toc - tic} seconds')
        return res
    return new_func


def encode(word):
    """
    :return: The word without accents, in uppercase, etc
    """
    ascii_name = normalize("NFKD", word).encode("ascii", errors="ignore").decode("ascii")
    return ascii_name.upper()


def get_gender_data():
    """
    :return: A dictionary with names and its allow
    """
    with open('data/nomes.csv') as name_and_gender_file:
        name_and_gender_reader = DictReader(name_and_gender_file)
        return {data["first_name"]: data["classification"] for data in name_and_gender_reader}


def get_filters(filename):
    """
    :type filename: str
    :return: A list with the normalized filters of file
    """
    filters = []
    with open(filename) as c:
        r = reader(c)
        for rrow in r:
            filters.append(encode(rrow[0]))
        return filters


def get_name_and_gender(person):
    """
    :type person: str
    :return: the likely main name and info if should pass or not of person
    :rtype: tuple
    """
    encoded_names = encode(person).split()
    ng = None
    for n in encoded_names:
        if n in gender_data.keys():
            ng = n, gender_data[n]
            break
    if not ng:
        ng = encoded_names[0], 'F'
    if ng[0] in pass_names:
        ng = ng[0], 'F'
        passed.append([ng[0], person])
    elif ng[0] in block_names:
        ng = ng[0], 'M'
        blocked.append([ng[0], person])
    return ng
