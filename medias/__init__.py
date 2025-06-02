import os

_CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def _local_resource(filename: str):
    return os.path.join(_CUR_DIR, filename)


ARIAL_TTF_PATH = _local_resource("arial.ttf")
