import contextlib


@contextlib.contextmanager
def output_header(text):
    assert text is not None
    try:
        print(f'{text} output =================>')
        yield
    finally:
        print(f'<================= {text} output')
