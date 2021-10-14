import logging
import falcon
import time
import urllib

def fmt_duration(nanos):
    if nanos < 500:
        return f"{nanos:.2f} ns"
    elif nanos < 500000:
        return f"{nanos / 1000:.2f} us"
    elif nanos < 500000000:
        return f"{nanos / 1000000:.2f} ms"
    else:
        return f"{nanos / 1000000000:.2f} s"

def timeit(operation, loggerName):
    logger = logging.getLogger(loggerName)
    def inner(func):
        def wrapper(*args, **kwargs):
            start = time.monotonic_ns()
            result = func(*args, **kwargs)
            end = time.monotonic_ns()
            logger.info(f"{operation} took {fmt_duration(end - start)} ")
            return result
        
        return wrapper
    return inner


def req_handler(operation, loggerName):
    logger = logging.getLogger(loggerName)
    def inner(func):
        @timeit(operation, loggerName)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except falcon.HTTPError as e:
                logger.warn(f"{operation} ended with {e}")
                raise
            except Exception as e:
                logger.error(f"{operation} failed! Error: {e}", exc_info=True)
                raise
        return wrapper
    return inner

def buildTermFilter(field, values):
    fieldFilters = []

    for value in values.split(','):
        if value:
            fieldFilters.append({'term': {field: value}})

    # need to simulate a boolean or over the filters
    # of the same field
    if fieldFilters:
        fieldFilters = {
            'bool': {
                'should': fieldFilters,
                'minimum_should_match': 1
            }
        }

    return fieldFilters

def parseFilters(req):
    authors = urllib.parse.unquote(req.params['authors']) if 'authors' in req.params else ""
    types = urllib.parse.unquote(req.params['types']) if 'types' in req.params else ""
    volumes = urllib.parse.unquote(req.params['volumes']) if 'volumes' in req.params else ""
    books = urllib.parse.unquote(req.params['books']) if 'books' in req.params else ""

    filters = []

    fieldFilters = [
        buildTermFilter('author', authors),
        buildTermFilter('type', types),
        buildTermFilter('volume', volumes),
        buildTermFilter('book', books)
    ]

    for fieldFilter in fieldFilters:
        if fieldFilter:
            filters.append(fieldFilter)

    return {
        'bool': {
            'must': filters
        }
    }