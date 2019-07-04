import contextlib


@contextlib.contextmanager
def output_header(text):
    try:
        print("{} output =================>\n".format(text))
        yield
    finally:
        print("\n<================= {} output".format(text))
