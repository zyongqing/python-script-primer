#!/usr/bin/env python
import functools
import logging

logging.basicConfig(format="%(levelname)s\t%(asctime)s\t%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def plugin(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        logger.debug("init pipeline %s", f.__name__)
        for each in f(*args, **kwargs):
            logger.debug('%s => "%s"', f.__name__, each)
            yield each
    return wrapper


@plugin
def one(pipeline):
    return (i for i in pipeline)


@plugin
def two(pipeline):
    return (i for i in pipeline)


@plugin
def three(pipeline):
    print(list(pipeline))
    yield "finished"


ops = [one, two, three]
pre_pipeline = range(10)

for pipeline in ops:
    pre_pipeline = pipeline(pre_pipeline)

for _ in pre_pipeline:
    pass
