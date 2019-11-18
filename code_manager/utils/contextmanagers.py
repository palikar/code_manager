import contextlib


@contextlib.contextmanager
def output_header(text):
    assert text is not None
    try:
        print("{} output =================>".format(text))
        yield
    finally:
        print("<================= {} output".format(text))
