import re
import time


def sleep(timeout, time_append=0, retry=3, match=None):
    def the_real_decorator(function):
        def wrapper(*args, **kwargs):
            retries = 0
            appended = 0
            while retries < retry:
                try:
                    return function(*args, **kwargs)
                except Exception as err:
                    if match is not None:
                        if not re.match(match, str(err), re.M | re.I):
                            raise err
                    print(f'Sleeping and retry for {timeout + appended} seconds. {function.__name__} {args} {str(err)}')
                    time.sleep(timeout + appended)
                    appended += time_append
                    retries += 1

        return wrapper

    return the_real_decorator


@sleep(1, time_append=3, match="^test")
def test(val):
    raise Exception("testadf")


if __name__ == '__main__':
    test("asdf")
