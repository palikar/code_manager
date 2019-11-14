class lazy_property():  # pylint: disable=invalid-name,too-few-public-methods

    def __init__(self, method):
        self._method = method
        self.__name__ = method.__name__
        self.__doc__ = method.__doc__

    def __get__(self, input_obj, cls=None):
        if input_obj is None:
            return None

        reset_function_name = self.__name__ + "__reset"

        if not hasattr(input_obj, reset_function_name):
            def reset_function():
                setattr(input_obj, self.__name__, self)
                del input_obj.__dict__[self.__name__]  # force "__get__" being called
            input_obj.__dict__[reset_function_name] = reset_function

        result = self._method(input_obj)
        input_obj.__dict__[self.__name__] = result
        return result
